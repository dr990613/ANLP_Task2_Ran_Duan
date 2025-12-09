# src/config.py
import os
from langchain_openai import ChatOpenAI

# 基础配置：与学院 vLLM / liteLLM 服务保持一致
BASE_URL = os.getenv("LITELLM_BASE_URL", "http://a6k2.dgx:34000/v1")
API_KEY = os.getenv("LITELLM_API_KEY", "sk-3ytNnX-OUrY4WQmGwJBmQA")  # 建议通过环境变量提供真实 Token
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-32b")


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    """
    返回一个配置好的 ChatOpenAI 实例。
    后续所有 Agent 统一通过这个函数获取 LLM。
    """
    if not API_KEY:
        # 这里不直接抛错，而是让调用方在第一次调用时发现问题并修复
        # 实际开发中也可以改成 raise RuntimeError("LITELLM_API_KEY is not set")
        print("[config] Warning: LITELLM_API_KEY is empty, please set environment variable.")

    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_base=BASE_URL,   # 使用 OpenAI 兼容的 base URL
        openai_api_key=API_KEY,
        temperature=temperature,
    )
    return llm
