import os
from openai import OpenAI
#test for using VPN and LLM

BASE_URL = os.getenv("LITELLM_BASE_URL", "http://a6k2.dgx:34000/v1")
API_KEY = os.getenv("LITELLM_API_KEY", "sk-3ytNnX-OUrY4WQmGwJBmQA")  # 你的学院 LLM Token
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-32b")


client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!What I should during the bad day?"}
    ]
)

print(response.choices[0].message.content)
