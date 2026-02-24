import time
import re
from crewai import Crew, Process
from agents import supervisor, issue_analyzer, code_suggester, security_reviewer, pr_drafter
from tasks import build_tasks


def run_crew(repo_name: str, issue_number: int, max_retries: int = 3) -> dict:
    tasks = build_tasks(repo_name, issue_number)

    crew = Crew(
        agents=[issue_analyzer, code_suggester, security_reviewer, pr_drafter],
        tasks=tasks,
        process=Process.hierarchical,
        manager_agent=supervisor,
        verbose=True,
        memory=True,
        max_rpm=1,  # ✅ FIX: reduced from 2 → 1 RPM to space out calls more aggressively
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🔁 Attempt {attempt}/{max_retries}...")
            start = time.time()
            result = crew.kickoff()
            elapsed = round(time.time() - start, 2)

            total_tokens = 0
            if result.token_usage:
                total_tokens = getattr(result.token_usage, "total_tokens", 0)

            return {
                "result": result.raw,
                "tasks_output": [str(t) for t in result.tasks_output],
                "token_usage": total_tokens,
                "elapsed_seconds": elapsed,
                "success": "PR created" in str(result.raw)
            }

        except Exception as e:
            last_error = e
            error_str = str(e)

            # ✅ FIX: check for both "rate_limit" and "tokens" keywords
            # Groq TPM errors contain "tokens" in the error type field
            if "rate_limit" in error_str.lower() or "tokens" in error_str.lower() or "ratelimiterror" in error_str.lower():

                # ✅ FIX: default wait is now 65s (TPM resets every 60s on Groq)
                wait = 65
                try:
                    # Groq message format: "Please try again in 14.02s"
                    match = re.search(r"try again in (\d+\.?\d*)s", error_str)
                    if match:
                        parsed_wait = float(match.group(1))
                        # ✅ FIX: always wait at least 65s for TPM errors (token bucket resets per minute)
                        wait = max(parsed_wait + 15, 65)
                except Exception:
                    pass

                print(f"⏳ Rate limit hit (TPM/RPM). Waiting {wait:.0f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait)
            else:
                raise e  # non-rate-limit error, don't retry

    raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")