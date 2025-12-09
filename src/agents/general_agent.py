# src/agents/general_agent.py
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_llm
from src.state import AgentState

llm = get_llm(temperature=0.3)

general_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a helpful general assistant focused on study, coding, and productivity.\n"
            "If the query does not clearly belong to theory, coding, or planning, "
            "you still try to provide a useful, concise answer.\n"
            "Prioritize clarity and practicality."
        ),
    ),
    (
        "user",
        (
            "User query:\n"
            "{query}\n\n"
            "Recent session history (may be empty):\n"
            "{history_text}"
        ),
    ),
])


def general_node(state: AgentState) -> AgentState:
    """
    兜底助手：
    - 处理无法被 Router 明确分类的问题
    - 提供与学习/生产力相关的通用建议
    """
    query = state.get("query", "").strip()
    history = state.get("session_history", [])

    if history:
        history_lines = []
        for turn in history[-5:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_lines.append(f"{role}: {content}")
        history_text = "\n".join(history_lines)
    else:
        history_text = ""

    chain = general_prompt | llm
    result = chain.invoke({"query": query, "history_text": history_text})

    state["partial_answer"] = result.content
    state.setdefault("activated_agents", []).append("general_agent")
    state.setdefault("tool_calls", [])
    return state
