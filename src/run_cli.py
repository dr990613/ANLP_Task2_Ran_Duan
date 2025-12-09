# src/run_cli.py
from typing import cast

from src.state import AgentState
from src.graph_builder import build_graph


def build_initial_state(query: str) -> AgentState:
    """
    构造初始的 AgentState。
    对于第一次运行，没有历史记录和用户档案；
    这些会在 memory_load_node 中从 memory.json 填充。
    """
    return {
        "query": query,
        "activated_agents": [],
        "tool_calls": [],
        # 下面三个字段会在 memory_load_node 中覆盖/填充
        "session_history": [],
        "user_profile": {},
        "notes": [],
    }


def run_single_query(app, query: str) -> AgentState:
    """
    对单个 query 调用 graph，并返回新的 state。
    """
    init_state = build_initial_state(query)
    result = cast(AgentState, app.invoke(init_state))
    return result


def interactive_loop():
    """
    简单的命令行交互循环：
    - 输入一条 query
    - 运行图
    - 打印最终答案 / 激活的 agents / 使用的工具
    - 输入 'exit' 或 Ctrl+C 退出
    """
    app = build_graph()
    print("Multi-Agent Study & Productivity Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            query = input("User> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Exiting]")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            print("[Exiting]")
            break

        state = run_single_query(app, query)

        print("\nAssistant>")
        print(state.get("final_answer", "").strip())

        activated = state.get("activated_agents", [])
        tools = state.get("tool_calls", [])

        if activated:
            print("\n[Activated agents]:", " -> ".join(activated))
        if tools:
            print("[Tools called]:", ", ".join(tools))

        print("-" * 60)


if __name__ == "__main__":
    interactive_loop()
