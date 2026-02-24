import streamlit as st
import threading
import queue
import sys
import io
from crew import run_crew

st.set_page_config(
    page_title="SRE Crew 🤖",
    page_icon="🔧",
    layout="wide"
)

st.title("🤖 Multi-Agent DevOps SRE Crew")
st.caption("Powered by CrewAI + Groq Llama 3.3 | Automates GitHub issue → PR pipeline")

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    repo_input = st.text_input(
        "GitHub Repo (owner/repo)",
        placeholder="e.g. torvalds/linux"
    )
    issue_input = st.number_input(
        "Issue Number",
        min_value=1,
        step=1,
        value=1
    )
    human_review = st.toggle("🧑 Require human approval before PR", value=False)
    run_btn = st.button("🚀 Run Crew", type="primary", use_container_width=True)


# ── Live Log Stream Helper ────────────────────────────────────────
class QueueStream(io.TextIOBase):
    """Redirects stdout/stderr into a thread-safe queue so Streamlit can read it."""
    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, msg: str):
        if msg.strip():
            self.q.put(msg)
        return len(msg)

    def flush(self):
        pass


def run_crew_in_thread(repo: str, issue: int, result_holder: list, q: queue.Queue):
    """Runs crew in a background thread, capturing stdout into the queue."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = QueueStream(q)
    sys.stderr = QueueStream(q)
    try:
        result = run_crew(repo, issue)
        result_holder.append({"success": True, "data": result})
    except Exception as e:
        result_holder.append({"success": False, "error": str(e)})
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        q.put("__DONE__")  # sentinel to signal completion


# ── Main Panel ────────────────────────────────────────────────────
if run_btn:
    if not repo_input:
        st.warning("Please enter a GitHub repo in the sidebar first.")
        st.stop()

    st.info("🚀 Crew is running! Live agent logs appear below in real time.")

    # Setup
    log_queue = queue.Queue()
    result_holder = []

    # Start crew in background thread
    thread = threading.Thread(
        target=run_crew_in_thread,
        args=(repo_input, int(issue_input), result_holder, log_queue),
        daemon=True
    )
    thread.start()

    # ── Live log display
    st.subheader("📡 Live Agent Logs")
    log_area = st.empty()
    log_lines = []

    # Poll queue until sentinel received
    while True:
        try:
            msg = log_queue.get(timeout=0.5)
            if msg == "__DONE__":
                break
            log_lines.append(msg)
            # Show last 60 lines to avoid huge text areas
            display = "\n".join(log_lines[-60:])
            log_area.code(display, language="bash")
        except queue.Empty:
            continue  # still running, keep polling

    thread.join()

    st.divider()

    # ── Results
    if not result_holder:
        st.error("❌ Crew returned no result. Check terminal for errors.")
    elif not result_holder[0]["success"]:
        st.error(f"❌ Crew failed: {result_holder[0]['error']}")
        st.info("Check your `.env` file for valid GITHUB_TOKEN and GROQ_API_KEY.")
    else:
        output = result_holder[0]["data"]

        # ── Metric Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Success", "Yes" if output["success"] else "No")
        col2.metric("⏱️ Time", f"{output['elapsed_seconds']}s")
        col3.metric("🪙 Tokens", output["token_usage"])

        st.divider()

        # ── Final Output
        st.subheader("📋 Final Output")
        st.markdown(output["result"])

        st.divider()

        # ── Step-by-step
        with st.expander("🔍 Step-by-step Agent Outputs", expanded=False):
            for i, task_out in enumerate(output["tasks_output"]):
                st.markdown(f"**Step {i + 1}:**")
                st.code(task_out, language="markdown")

        # ── Human fallback
        if human_review and not output["success"]:
            st.warning("⚠️ Human review required — agents could not auto-resolve.")
            feedback = st.text_area("Provide guidance for retry:")
            if st.button("🔁 Retry with guidance"):
                st.info("Re-running crew with your guidance...")
                output2 = run_crew(f"{repo_input} | Human hint: {feedback}", int(issue_input))
                st.markdown(output2["result"])
