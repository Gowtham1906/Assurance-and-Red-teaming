"""Probe candidate judge models: JSON compliance, latency, token usage."""
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
messages = [
    {"role": "system", "content": 'You are a strict evaluation judge. Return ONLY JSON: '
                                  '{"score": number 0..1, "rationale": short string}.'},
    {"role": "user", "content": 'Answer: "In pharma, lower OEE is normal because CIP/SIP cycles '
                                'use scheduled time."\nRequired key facts:\n- lower OEE is normal '
                                'in pharmaceutical\n- CIP/SIP cycles consume scheduled time\n'
                                'What fraction of the key facts does the answer convey?'},
]
for model in ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]:
    t = time.time()
    try:
        r = client.chat.completions.create(model=model, messages=messages, temperature=0, timeout=60)
        u = r.usage
        print(f"{model} | {time.time() - t:.1f}s | prompt {u.prompt_tokens} completion {u.completion_tokens}")
        print("   ", repr(r.choices[0].message.content[:240]))
    except Exception as exc:
        print(model, "ERROR", type(exc).__name__, str(exc)[:200])
