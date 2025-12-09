# src/dry_run_graph.py
"""
Dry run 检查脚本（不调用 LLM，不发请求）

作用：
1. 尝试构建并 compile 整个 LangGraph 图；
2. 打印图结构（ASCII），确认节点和边是否都连上；
3. 如果这里能运行到结束，说明：
   - 所有 import 没问题
   - AgentState / 节点函数签名没问题
   - graph_builder 里的拓扑结构合法
"""

from src.graph_builder import build_graph


def main():
    # 1. 构建并编译图
    app = build_graph()
    print("[Dry Run] Graph compiled successfully.\n")

    # 2. 获取底层 graph 对象（不执行 invoke）
    graph = app.get_graph()

    # 3. 打印 ASCII 结构，检查节点与流向
    print("[Dry Run] Graph structure (ASCII):")
    try:
        ascii_graph = graph.draw_ascii()
        print(ascii_graph)
    except Exception as e:
        print("[Dry Run] Failed to draw ASCII graph:", e)

    # 4. 打印节点列表，确认所有节点都在图中
    try:
        print("\n[Dry Run] Nodes in graph:")
        print(list(graph.nodes))
    except Exception:
        # 某些版本的 API 写法稍有不同，这里做个保护
        pass


if __name__ == "__main__":
    main()
