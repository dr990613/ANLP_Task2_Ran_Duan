# src/agents/coding_agent.py
import re
from langchain_core.prompts import ChatPromptTemplate
from src.config import get_llm
from src.state import AgentState
from src.tools import beacon_analyze_code

llm = get_llm(temperature=0.2)

coding_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a coding assistant focused on:\n"
            "- Python code\n"
            "- machine learning / deep learning frameworks\n"
            "- LangChain and LangGraph\n\n"
            "Your goals:\n"
            "1) Explain error messages and stack traces.\n"
            "2) Suggest concrete code fixes or refactors.\n"
            "3) When relevant, relate to multi-agent / LLM-based systems.\n"
            "4) Be concise but specific. Use code blocks where needed."
        ),
    ),
    (
        "user",
        (
            "User query (may include code and error messages):\n"
            "{query}\n\n"
            "Recent session history (may be empty):\n"
            "{history_text}"
        ),
    ),
])


def _extract_first_python_block(text: str) -> str | None:
    """
    从 LLM 的回答中提取第一个 Python 代码块。
    优先匹配 ```python ...```，若没有则匹配第一个 ``` ... ```。
    """
    # 优先匹配 ```python ... ``` 形式
    pattern_py = re.compile(r"```python\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    m = pattern_py.search(text)
    if m:
        code = m.group(1).strip()
        return code if code else None

    # 退而求其次，匹配任意 ``` ... ``` 代码块
    pattern_any = re.compile(r"```(.*?)```", re.DOTALL)
    m = pattern_any.search(text)
    if m:
        code = m.group(1).strip()
        return code if code else None

    return None


def coding_node(state: AgentState) -> AgentState:
    """
    使用 Qwen 处理与代码相关的问题：
    - 错误解释
    - 实现建议
    - 与 LangChain / LangGraph 相关的问题

    在生成回答后：
    - 尝试从回答中抽取 Python 代码块
    - 若成功，调用 beacon_analyze_code 做 Beacon 推理
    - 将 Beacon summary 附加到回答末尾，作为工程级提醒
    """
    query = state.get("query", "").strip()
    history = state.get("session_history", [])

    state.setdefault("tool_calls", [])
    state.setdefault("activated_agents", [])

    # 将近期历史压缩成一段文本，方便提供上下文
    if history:
        history_lines = []
        for turn in history[-5:]:  # 只取最近几条
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_lines.append(f"{role}: {content}")
        history_text = "\n".join(history_lines)
    else:
        history_text = ""

    # 1) 调用 LLM 生成 coding 回答
    chain = coding_prompt | llm
    result = chain.invoke({"query": query, "history_text": history_text})
    answer = result.content

    # 2) 从回答中提取代码块，调用 Beacon 推理
    code_block = _extract_first_python_block(answer)
    if code_block:
        try:
            beacon_summary = beacon_analyze_code(code_block)
            state["tool_calls"].append("beacon_analyze_code")

            # 将 Beacon summary 附加到回答末尾
            answer = answer.rstrip() + "\n\n---\n" + beacon_summary
        except Exception as e:
            # 即使 Beacon 工具异常，也不要让主回答崩掉
            answer = answer.rstrip() + f"\n\n[Beacon] Failed to analyze code: {e}"

    state["partial_answer"] = answer
    state["activated_agents"].append("coding_agent")
    return state
