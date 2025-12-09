# src/agents/router_agent.py
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_llm
from src.state import AgentState

llm = get_llm(temperature=0.0)

router_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a routing agent.\n"
            "IMPORTANT RULES:1. Ignore all history, memory, session context, previous answers.2. ONLY classify the CURRENT user query.3. Do NOT make assumptions based on past tasks.4. Always categorize the query into EXACTLY ONE label:\n"
            "- theory      : questions about theory, concepts, definitions (MAS, LLM agents, ML, RL, etc.)\n"
            "- coding      : questions about code, errors, implementation details, APIs, libraries.\n"
            "- planning    : questions about planning, scheduling, study plans, productivity routines.\n"
            "- general     : other questions that are still related to study or productivity.\n\n"
            "Output only the label, in lowercase, with no extra text."
        ),
    ),
    ("user", "{query}")
])


def router_node(state: AgentState) -> AgentState:
    """
    读取 state['query']，调用 Qwen 进行分类，
    将结果写入 state['route']，并记录当前节点。
    """
    query = state.get("query", "").strip()
    if not query:
        # 没有 query 时直接走 general
        state["route"] = "general"  # type: ignore
    else:
        chain = router_prompt | llm
        result = chain.invoke({"query": query})
        label = result.content.strip().lower()

        if label not in ["theory", "coding", "planning", "general"]:
            label = "general"

        state["route"] = label  # type: ignore

    state.setdefault("activated_agents", []).append("router")
    state.setdefault("tool_calls", [])
    return state
