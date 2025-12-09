# src/run_experiments.py
import json
from datetime import datetime
from pathlib import Path

from src.graph_builder import build_graph
from src.state import AgentState

# ================================
# 配置（你可以在这里改实验输入和输出文件名）
# ================================
EXPERIMENT_QUERIES = [
    # 1. 理论问题
    "What is the difference between a router-specialists MAS and a planner-executor MAS pattern?",

    # 2. 设计 / 架构问题
    "How should I design a multi-agent architecture if I want to integrate a vector database for memory?",

    # 3. 实现 / 编程问题
    "I am getting a KeyError in LangGraph when trying to access 'route'. How should I fix it?",

    # 4. 日常学习问题
    "Help me create a 7-day deep learning study plan focusing on CNNs.",

    # 5. 生产力问题
    "I only have 2 hours per day this week. Help me schedule my tasks efficiently."
]

OUTPUT_FILE = "experiment_results.json"


def build_initial_state(query: str) -> AgentState:
    """
    为每轮调用构造一个新的单轮会话 state。
    Memory 会在 memory_load_node 中加载。
    """
    return {
        "query": query,
        "activated_agents": [],
        "tool_calls": [],
        "session_history": [],
        "user_profile": {},
        "notes": []
    }


def run_single_query(app, query: str):
    """
    使用 graph app.invoke(state) 执行单条 query，返回结果 state。
    """
    init_state = build_initial_state(query)
    result_state = app.invoke(init_state)
    return result_state


def collect_memory_usage(result_state: AgentState):
    """
    分析 state 中的记忆使用方式，简单记录：
    - 使用了多少历史条目
    - 是否加载了 notes
    """
    return {
        "session_history_used": len(result_state.get("session_history", [])),
        "notes_loaded": len(result_state.get("notes", []))
    }


def run_experiments():
    # 构建 graph
    app = build_graph()

    # 收集所有实验结果
    all_results = []

    print("Running experiments...\n")

    for idx, query in enumerate(EXPERIMENT_QUERIES, 1):
        print(f"Running Query {idx}: {query}")

        # 调用 MAS
        result_state = run_single_query(app, query)

        # 收集信息
        record = {
            "query": query,
            "activated_agents": result_state.get("activated_agents", []),
            "tools_called": result_state.get("tool_calls", []),
            "final_answer": result_state.get("final_answer", ""),
            "memory_usage": collect_memory_usage(result_state),
            "raw_state": result_state,  # 完整 state（便于写报告）
        }

        all_results.append(record)

        print(f" → Activated agents: {record['activated_agents']}")
        print(f" → Tools called: {record['tools_called']}")
        print(f" → Memory used: {record['memory_usage']}")
        print("-" * 50)

    # 保存 JSON
    output_path = Path(OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nExperiment results saved to: {output_path.absolute()}")


if __name__ == "__main__":
    run_experiments()
