# src/agents/memory_agent.py
import json
from pathlib import Path
from typing import Dict, Any, List

from src.state import AgentState

# 项目根目录: .../multi_agent_study_assistant/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEMORY_PATH = PROJECT_ROOT / "data" / "memory.json"


def _load_memory_file() -> Dict[str, Any]:
    """
    从 data/memory.json 加载长期记忆。
    如果文件不存在，则返回一个空模板。
    """
    if not MEMORY_PATH.exists():
        return {
            "user_profile": {},
            "history": [],
            "notes": []
        }

    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 如果文件损坏，回退到空模板，避免整个系统崩溃
        return {
            "user_profile": {},
            "history": [],
            "notes": []
        }


def _save_memory_file(data: Dict[str, Any]) -> None:
    """
    将长期记忆写回 data/memory.json。
    """
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def memory_load_node(state: AgentState) -> AgentState:
    """
    在图的入口被调用：
    - 从 memory.json 中读取 user_profile / history / notes
    - 将最近若干条历史写入 state['session_history']
    """
    data = _load_memory_file()

    user_profile = data.get("user_profile", {})
    history: List[Dict[str, str]] = data.get("history", [])
    notes: List[str] = data.get("notes", [])

    # 可以只保留最近 N 条历史，避免 prompt 太长
    recent_history = history[-2:]

    state["user_profile"] = user_profile
    state["session_history"] = recent_history
    state["notes"] = notes

    state.setdefault("activated_agents", []).append("memory_load")
    state.setdefault("tool_calls", [])
    return state


def memory_update_node(state: AgentState) -> AgentState:
    data = _load_memory_file()
    history: List[Dict[str, str]] = data.get("history", [])

    query = state.get("query", "")
    answer = state.get("final_answer") or state.get("partial_answer") or ""

    if query:
        history.append({"role": "user", "content": query})
    if answer:
        history.append({"role": "assistant", "content": answer})

    # 控制文件中的历史长度
    data["history"] = history[-50:]

    # ✅ 同时更新当前 state 的 session_history（满足“state fields accumulate previous Q/A”）
    state_history = state.get("session_history", [])
    if query:
        state_history.append({"role": "user", "content": query})
    if answer:
        state_history.append({"role": "assistant", "content": answer})
    state["session_history"] = state_history[-10:]

    data.setdefault("user_profile", state.get("user_profile", {}))
    data.setdefault("notes", state.get("notes", []))

    _save_memory_file(data)

    state.setdefault("activated_agents", []).append("memory_update")
    return state

