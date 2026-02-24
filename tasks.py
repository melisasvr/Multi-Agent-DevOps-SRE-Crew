from crewai import Task
from agents import issue_analyzer, code_suggester, security_reviewer, pr_drafter


def build_tasks(repo_name: str, issue_number: int) -> list:

    # ✅ FIX: All task descriptions trimmed to reduce prompt token usage.
    # Verbose instructions were inflating each prompt by 100-200 tokens.
    # Rule of thumb: keep each description under 60 words.

    analyze_task = Task(
        description=(
            f"Fetch issue #{issue_number} from repo '{repo_name}' using the fetch_github_issue tool. "
            "Do NOT use web search. "
            "Return root cause, affected files, severity (low/medium/high), and confidence score 0-1."
        ),
        expected_output="JSON: root_cause, affected_files, severity, confidence",
        agent=issue_analyzer,
    )

    suggest_task = Task(
        description=(
            "Using only the issue analysis in context, propose a minimal code fix. "
            "Do NOT use search tools. "
            "Include filename, line numbers if known, and a unified diff or clear description."
        ),
        expected_output="Code diff or patch with brief explanation.",
        agent=code_suggester,
        context=[analyze_task]
    )

    review_task = Task(
        description=(
            "Review the proposed fix from context. "
            "Do NOT use search tools. "
            "Flag security issues, hardcoded secrets, or logic errors. "
            "Output approved=True/False and issues found."
        ),
        expected_output="JSON: approved, issues_found, revised_patch (if any)",
        agent=security_reviewer,
        context=[suggest_task]
    )

    pr_task = Task(
        description=(
            f"Open a PR in '{repo_name}' on branch 'sre-crew/fix-issue-{issue_number}' "
            "using the create_pull_request tool. "
            "Then comment on the issue using post_issue_comment. "
            "Do NOT use search tools."
        ),
        expected_output="PR URL and comment confirmation.",
        agent=pr_drafter,
        context=[review_task]
    )

    return [analyze_task, suggest_task, review_task, pr_task]