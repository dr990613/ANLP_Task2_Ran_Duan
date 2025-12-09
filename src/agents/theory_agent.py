# src/agents/theory_agent.py
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_llm
from src.state import AgentState
from src.tools import search_notes, save_markdown_note

llm = get_llm(temperature=0.3)

theory_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a theory explainer for:\n"
            "- multi-agent systems (MAS) and LLM-based agents\n"
            "- machine learning and deep learning\n"
            "- reinforcement learning and related topics\n\n"
            "Your goals:\n"
            "1) Explain concepts clearly and concisely.\n"
            "2) Use step-by-step structure when helpful.\n"
            "3) If relevant notes are provided, integrate them into your answer.\n"
        ),
    ),
    (
        "user",
        (
            "User query:\n"
            "{query}\n\n"
            "Relevant notes (may be empty):\n"
            "{notes_text}"
        ),
    ),
])


def theory_node(state: AgentState) -> AgentState:
    """
    使用 Qwen 解释 MAS / LLM / ML / RL 等相关理论问题。
    如果 state['notes'] 中有相关内容，则先用 search_notes 做简单检索，
    将结果注入到 prompt 中。
    回答生成后，调用 save_markdown_note 将解释内容保存为一份 markdown 笔记。
    """
    query = state.get("query", "").strip()
    notes_list = state.get("notes", [])

    state.setdefault("tool_calls", [])
    state.setdefault("activated_agents", [])

    # 1) 检索 notes
    notes_text = ""
    if notes_list:
        notes_text = search_notes(query, notes_list, max_results=2)
        if notes_text:
            state["tool_calls"].append("search_notes")

    # 2) 调用 LLM 生成理论解释
    chain = theory_prompt | llm
    result = chain.invoke({"query": query, "notes_text": notes_text})
    answer = result.content

    # 3) 保存为 markdown 笔记
    try:
        # 用 query 作为标题（简单处理）
        title = query if query else "Theory_Notes"
        md_path = save_markdown_note(title=title, content=answer, base_dir="notes")
        state["tool_calls"].append("save_markdown_note")

        # 在回答末尾追加一个轻量提示（也方便实验记录）
        answer = answer.rstrip() + f"\n\n_(Saved as markdown note: {md_path})_"
        # 可选：把路径写进 state，方便你后续分析
        state["markdown_note_path"] = md_path  # type: ignore
    except Exception as e:
        # 不让 agent 崩掉，最多在回答末尾加一句告警
        answer = answer.rstrip() + f"\n\n[Warning] Failed to save markdown note: {e}"

    state["partial_answer"] = answer
    state["activated_agents"].append("theory_agent")
    return state
