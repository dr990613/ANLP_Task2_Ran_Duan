# src/state.py
from typing import TypedDict, List, Dict, Any, Optional, Literal

# 路由类别：Router 会在这几个标签之间选择
RouteType = Literal["theory", "coding", "planning", "general"]


class AgentState(TypedDict, total=False):
    """
    多智能体系统的共享状态结构。
    所有 LangGraph 节点都读写这个 TypedDict。
    """

    # 1. 用户输入
    query: str  # 当前用户查询

    # 2. 中间结果
    route: RouteType                 # Router 的分类结果
    partial_answer: Optional[str]    # 某个专家智能体产生的回答
    plan: Optional[str]              # Planner 生成的学习/任务计划

    activated_agents: List[str]      # 本次调用中依次被激活的节点名称
    tool_calls: List[str]            # 本次调用中使用过的工具名称

    # 3. 记忆相关
    session_history: List[Dict[str, str]]  # 当前会话的历史 Q&A（从长期记忆中截取）
    user_profile: Dict[str, Any]           # 用户档案，如专业/课程/目标
    notes: List[str]                       # 简单的笔记列表，用于 search_notes 工具

    # 4. 最终输出
    final_answer: Optional[str]     # 最终返回给用户的答案
