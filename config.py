from crewai import LLM
from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
    max_tokens=512   # ✅ FIX: reduced from 1024 → 512 to stay within 6000 TPM limit
                     # 4 agents × ~512 tokens = ~2048 max per run (safe headroom)
)

gh = Github(os.getenv("GITHUB_TOKEN"))