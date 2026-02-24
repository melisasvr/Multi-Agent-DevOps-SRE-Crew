from dotenv import load_dotenv
import os
load_dotenv()

from crewai import LLM

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
    max_tokens=512   # ✅ FIX: match config.py
)

response = llm.call([{"role": "user", "content": "Say hello in one word."}])
print("LLM response:", response)