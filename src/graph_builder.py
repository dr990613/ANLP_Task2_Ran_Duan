# src/graph_builder.py
from typing import Callable

from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.memory_agent import memory_load_node, memory_update_node
from src.agents.router_agent import router_node
from src.agents.theory_agent import theory_node
from src.agents.coding_agent import coding_node
from src.agents.planner_agent import planner_node
from src.agents.general_agent import general_node


def route_selector(state: AgentState) -> str:
    """
    LangGraph 条件路由函数。
    根据 state['route'] 的值决定下一步走向哪个专家节点。
    """
    route = state.get("route", "general")
    if route not in {"theory", "coding", "planning", "general"}:
        return "general"
    return route


def output_node(state: AgentState) -> AgentState:
    """
    输出节点：将 partial_answer 作为 final_answer。
    """
    final_answer = state.get("partial_answer") or state.get("final_answer") or ""
    state["final_answer"] = final_answer

    state.setdefault("activated_agents", []).append("output_node")
    state.setdefault("tool_calls", [])
    return state


def build_graph():
    """
    新的工作流结构（符合最新设计）：

        router
            → memory_load
                → theory/coding/planning/general
                    → memory_update
                        → output
                            → END
    """

    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("router", router_node)
    graph.add_node("memory_load", memory_load_node)

    graph.add_node("theory", theory_node)
    graph.add_node("coding", coding_node)
    graph.add_node("planning", planner_node)
    graph.add_node("general", general_node)

    graph.add_node("memory_update", memory_update_node)
    graph.add_node("output", output_node)

    # 入口节点 → router（防止 memory 污染 Router 的判断）
    graph.set_entry_point("router")

    # router → memory_load
    graph.add_edge("router", "memory_load")

    # memory_load → 条件路由（根据分类跳转正确专家）
    graph.add_conditional_edges(
        "memory_load",
        route_selector,
        {
            "theory": "theory",
            "coding": "coding",
            "planning": "planning",
            "general": "general",
        },
    )

    # 专家 → memory_update
    for node_name in ["theory", "coding", "planning", "general"]:
        graph.add_edge(node_name, "memory_update")

    # memory_update → output → END
    graph.add_edge("memory_update", "output")
    graph.add_edge("output", END)

    return graph.compile()
