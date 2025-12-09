# src/agents/planner_agent.py
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_llm
from src.state import AgentState

llm = get_llm(temperature=0.4)

planner_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a study and productivity planner.\n"
            "You help the user turn vague goals into concrete step-by-step plans.\n\n"
            "Guidelines:\n"
            "- Ask yourself: what is the realistic next steps for this user?\n"
            "- Use bullet lists or numbered steps.\n"
            "- When possible, split into days or sessions.\n"
            "- Keep the plan realistic for a busy student in a master's program."
        ),
    ),
    (
        "user",
        (
            "User query:\n"
            "{query}\n\n"
            "User profile (may be empty):\n"
            "{profile_text}\n\n"
            "Recent session history (may be empty):\n"
            "{history_text}"
        ),
    ),
])


def planner_node(state: AgentState) -> AgentState:
    """
    将用户的学习/工作目标拆解为计划：
    - 使用 user_profile 中的信息（专业、当前课程、目标等）
    - 参考最近的 session_history（如已有提到的任务）
    """
    query = state.get("query", "").strip()
    user_profile = state.get("user_profile", {})
    history = state.get("session_history", [])

    # 将 user_profile 转为简单文本
    if user_profile:
        profile_lines = [f"{k}: {v}" for k, v in user_profile.items()]
        profile_text = "\n".join(profile_lines)
    else:
        profile_text = "No profile information available."

    # 将近期历史压缩成一段文本
    if history:
        history_lines = []
        for turn in history[-5:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_lines.append(f"{role}: {content}")
        history_text = "\n".join(history_lines)
    else:
        history_text = "No recent history."

    chain = planner_prompt | llm
    result = chain.invoke(
        {
            "query": query,
            "profile_text": profile_text,
            "history_text": history_text,
        }
    )

    plan_text = result.content
    state["plan"] = plan_text
    state["partial_answer"] = plan_text

    state.setdefault("activated_agents", []).append("planner_agent")
    state.setdefault("tool_calls", [])
    return state
