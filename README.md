# 🤖 Multi-Agent DevOps SRE Crew

> A collaborative AI crew that ingests a GitHub issue, analyzes root cause, suggests and reviews code fixes, then autonomously drafts a pull request with human fallback at every critical step.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![CrewAI](https://img.shields.io/badge/CrewAI-1.9.3-green)
![Groq](https://img.shields.io/badge/Groq-Llama3.1-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 What It Does

You give it a GitHub repo and an issue number. The AI crew takes over:

1. **Fetches** the issue from GitHub
2. **Analyzes** the root cause
3. **Suggests** a code fix
4. **Reviews** it for security issues
5. **Opens a Pull Request** automatically
6. **Posts a comment** on the original issue linking the PR

All of this happens autonomously, with a live Streamlit UI showing every step.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│           (repo input + live logs + results)             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Supervisor Agent                         │
│         (orchestrates, delegates, retries)               │
└──┬──────────┬──────────────┬──────────────┬─────────────┘
   │          │              │              │
   ▼          ▼              ▼              ▼
Issue      Code          Security        PR
Analyzer   Suggester     Reviewer        Drafter
   │          │              │              │
Fetches    Generates     Audits code    Creates branch
GitHub     patch/diff    for vulns      + opens PR
issue                                  + comments
                                       on issue
```

**Process type:** Hierarchical (Supervisor delegates and validates each step)

**Retry logic:** Up to 3 attempts per run with 15-second backoff on rate limits

---

## 🤖 Agents & Roles

| Agent | Role | Tools |
|---|---|---|
| **Supervisor** | Orchestrates the crew, delegates tasks, handles retries | None (delegation only) |
| **Issue Analyzer** | Fetches and analyzes the GitHub issue, identifies root cause | `FetchIssueTool` |
| **Code Suggester** | Generates code diffs and patches based on the analysis | None (LLM reasoning) |
| **Security Reviewer** | Scans suggested code for vulnerabilities and anti-patterns | None (LLM reasoning) |
| **PR Drafter** | Creates branch, opens PR, posts comment on original issue | `CreatePRTool`, `PostCommentTool` |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **CrewAI 1.9.3** | Multi-agent orchestration framework |
| **Groq (Llama 3.1 8B Instant)** | Fast LLM inference |
| **LiteLLM** | LLM routing layer used by CrewAI |
| **PyGitHub** | GitHub API — issues, branches, PRs, comments |
| **Streamlit** | Web UI for input and live output |
| **python-dotenv** | Environment variable management |

---

## 📁 Project Structure

```
Multi-Agent DevOps SRE Crew/
│
├── app.py                  # Streamlit UI
├── crew.py                 # Crew assembly and kickoff
├── agents.py               # Agent definitions
├── tasks.py                # Task definitions
├── config.py               # LLM + GitHub client setup
├── test_llm.py             # LLM connection sanity check
├── .env                    # API keys (never commit this!)
├── requirements.txt        # Python dependencies
│
└── tools/
    ├── __init__.py         # Makes tools a Python package
    └── github_tools.py     # Custom GitHub tools
```

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/sre-crew.git
cd sre-crew
```

### 2. Install dependencies

```bash
pip install "crewai[tools]" litellm langchain-groq PyGitHub streamlit python-dotenv
```

### 3. Set up your `.env` file

```ini
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Never add quotes around values in `.env` files

### 4. Verify your LLM connection

```bash
python test_llm.py
# Expected: LLM response: Hello.
```

### 5. Launch the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🔑 GitHub Token Permissions

- Your GitHub token needs these permissions for the crew to create branches and PRs:

```
✅ Contents       → Read and Write
✅ Issues         → Read and Write
✅ Pull Requests  → Read and Write
```

- Generate at: **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**

---

## 🖥️ How to Use

1. Enter your GitHub repo in the format `owner/repo`
2. Enter the issue number you want to resolve
3. Optionally toggle **Human Approval** to review before PR is created
4. Click **🚀 Run Crew**
5. Watch live agent logs stream in real time
6. View the final PR link and step-by-step agent outputs

---

## ⚠️ Known Limitations & Fixes
- **Groq Rate Limits (Free Tier)**
- The free tier has token-per-minute limits. The crew uses `max_rpm=3` and `llama-3.1-8b-instant` to stay within limits. If you hit a rate limit, wait 15 seconds and retry.
- **LLM Hallucinating File Paths**
- The agents may suggest fixes for files that don't exist in the repo. This is expected on small/empty repos. Use a repo with real code for best results.
- **PR Branch Already Exists**
- If you run the crew twice on the same issue, the branch creation will fail. Either delete the branch manually on GitHub or the crew will report the existing PR URL.
- **signal/SIGTERM Warnings in Streamlit**
- You may see `Cannot register SIGTERM handler` warnings in the terminal. These are harmless and come from CrewAI's telemetry system running in Streamlit's thread.

---

## 🧠 Why Multi-Agent?

| Single Agent | Multi-Agent Crew |
|---|---|
| One long prompt does everything | Each agent has one focused job |
| No retry granularity | Supervisor retries individual steps |
| Security mixed with code generation | Dedicated Security Reviewer catches issues |
| Hard to debug | Each agent's output is logged separately |
| Hallucinations compound | Each agent validates the previous one |

---

## 📦 Requirements

```
crewai>=1.9.0
crewai-tools
litellm
langchain-groq
PyGitHub
streamlit
python-dotenv
```

Install all at once:
```bash
pip install "crewai[tools]" litellm langchain-groq PyGitHub streamlit python-dotenv
```

---

## 🗺️ Roadmap

- [ ] LangGraph integration for persistent state across sessions
- [ ] Support for multiple issues in one run
- [ ] Slack notification when PR is created
- [ ] Confidence threshold with human-in-the-loop approval flow
- [ ] Eval dashboard (success rate, token cost, time per issue)
- [ ] Support for GitLab and Bitbucket

---

## 📄 License

- MIT License — free to use, modify, and distribute.
```
Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including, without limitation, the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
---

## 🤝 Contributing
- Contributions are very welcome! If you'd like to collaborate on this project, feel free to:
- Fork the repository and submit a Pull Request
- Open an issue if you find a bug or have a feature idea
- Suggest improvements to the agent pipeline, UI, or documentation
- Share the project with others who might find it useful
- Whether it's a small fix, a new feature, or a completely new idea, all contributions are appreciated. Let's build something great together! 🚀

---

## 🙏 Built With

- [CrewAI](https://crewai.com) — Multi-agent framework
- [Groq](https://console.groq.com) — Ultra-fast LLM inference
- [Streamlit](https://streamlit.io) — Python web UI
- [PyGitHub](https://pygithub.readthedocs.io) — GitHub API client
