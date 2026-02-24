from crewai import Agent
from config import llm
from tools.github_tools import FetchIssueTool, CreatePRTool, PostCommentTool

fetch_tool = FetchIssueTool()
pr_tool = CreatePRTool()
comment_tool = PostCommentTool()

# ✅ FIX: max_iter reduced across all agents to limit total LLM calls per run.
# Every extra iteration = more tokens burned against the 6000 TPM limit.

supervisor = Agent(
    role="DevOps Supervisor",
    goal="Orchestrate agents to resolve GitHub issues end-to-end.",
    backstory="Senior SRE with 10 years managing incident response pipelines.",
    llm=llm,
    allow_delegation=True,
    verbose=True,
    max_iter=3,   # ✅ FIX: reduced from 5 → 3
    tools=[]
)

issue_analyzer = Agent(
    role="Issue Analyzer",
    goal="Parse and understand the GitHub issue to produce a structured root-cause analysis.",
    backstory="Expert in reading bug reports, stack traces, and GitHub issue threads.",
    tools=[fetch_tool],
    llm=llm,
    verbose=True,
    max_iter=2    # ✅ FIX: reduced from 3 → 2
)

code_suggester = Agent(
    role="Code Suggester",
    goal="Generate precise code diffs or file patches to resolve the analyzed issue.",
    backstory="Senior Python/DevOps engineer who writes minimal, clean fixes.",
    llm=llm,
    verbose=True,
    tools=[],
    max_iter=2    # ✅ FIX: reduced from 3 → 2
)

security_reviewer = Agent(
    role="Security Reviewer",
    goal="Audit suggested code for vulnerabilities, hardcoded secrets, or regressions.",
    backstory="AppSec engineer trained on OWASP Top 10 and CVE databases.",
    llm=llm,
    verbose=True,
    tools=[],
    max_iter=2    # ✅ FIX: reduced from 3 → 2
)

pr_drafter = Agent(
    role="PR Drafter",
    goal="Create a well-documented PR with the approved fix and notify the issue author.",
    backstory="Technical writer and GitHub power user.",
    tools=[pr_tool, comment_tool],
    llm=llm,
    verbose=True,
    max_iter=2    # ✅ FIX: reduced from 3 → 2
)