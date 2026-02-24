from crewai.tools import BaseTool
from github import Github
from dotenv import load_dotenv
import os

load_dotenv()
gh = Github(os.getenv("GITHUB_TOKEN"))

class FetchIssueTool(BaseTool):
    name: str = "fetch_github_issue"
    description: str = "Fetches a GitHub issue body, labels, and comments."

    def _run(self, repo_name: str, issue_number: int) -> str:
        try:
            repo = gh.get_repo(repo_name)
            issue = repo.get_issue(int(issue_number))
            comments = [c.body for c in issue.get_comments()]
            return (
                f"Title: {issue.title}\n"
                f"Body: {issue.body}\n"
                f"Labels: {[l.name for l in issue.labels]}\n"
                f"Comments: {comments}"
            )
        except Exception as e:
            return f"Error fetching issue: {str(e)}"


class CreatePRTool(BaseTool):
    name: str = "create_pull_request"
    description: str = "Creates a branch and opens a PR."

    def _run(self, repo_name: str, title: str, body: str, branch_name: str, base: str = "main") -> str:
        try:
            repo = gh.get_repo(repo_name)
            source = repo.get_branch(base)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base
            )
            return f"PR created: {pr.html_url}"
        except Exception as e:
            return f"Error creating PR: {str(e)}"


class PostCommentTool(BaseTool):
    name: str = "post_issue_comment"
    description: str = "Posts a comment on a GitHub issue."

    def _run(self, repo_name: str, issue_number: int, comment: str) -> str:
        try:
            repo = gh.get_repo(repo_name)
            issue = repo.get_issue(int(issue_number))
            issue.create_comment(comment)
            return "Comment posted successfully."
        except Exception as e:
            return f"Error posting comment: {str(e)}"