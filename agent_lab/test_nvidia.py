import os
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)

response = client.chat.completions.create(
    model="nvidia/nemotron-3-nano-30b-a3b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: AGENT LAB ONLINE",
        }
    ],
    max_tokens=128,
    temperature=0,
)

print("MODEL:", response.model)
print("ROLE:", response.choices[0].message.role)
print("CONTENT:", repr(response.choices[0].message.content))
print("FINISH:", response.choices[0].finish_reason)