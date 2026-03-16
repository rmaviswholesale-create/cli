"""
Ollama Power Agent — shell, code exec, web scrape/crawl, subagents

Setup:
  pip install -r requirements.txt
  ollama serve
  python agent.py
"""

import asyncio
import subprocess
import textwrap
import urllib.request
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL    = "llama3.2"
OLLAMA_API_KEY  = "0f92d714722747c797c5d71d1230cce6"

ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
set_default_openai_client(ollama_client)

# ---------------------------------------------------------------------------
# Tool: run shell command
# ---------------------------------------------------------------------------
def run_shell(command: str) -> str:
    """Run a shell command and return stdout + stderr. Timeout 30s."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        parts = []
        if out:
            parts.append(f"stdout:\n{out}")
        if err:
            parts.append(f"stderr:\n{err}")
        parts.append(f"exit_code: {result.returncode}")
        return "\n".join(parts) or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30s"
    except Exception as exc:
        return f"Error: {exc}"

# ---------------------------------------------------------------------------
# Tool: execute Python code
# ---------------------------------------------------------------------------
def run_python(code: str) -> str:
    """Execute Python code and return printed output + return value."""
    stdout_buf = StringIO()
    stderr_buf = StringIO()
    local_ns: dict = {}
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(textwrap.dedent(code), local_ns)  # noqa: S102
        out = stdout_buf.getvalue().strip()
        err = stderr_buf.getvalue().strip()
        result = local_ns.get("result")
        parts = []
        if out:
            parts.append(out)
        if err:
            parts.append(f"stderr: {err}")
        if result is not None:
            parts.append(f"result = {result!r}")
        return "\n".join(parts) or "(no output)"
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"

# ---------------------------------------------------------------------------
# Tool: scrape a URL (plain text)
# ---------------------------------------------------------------------------
def scrape_url(url: str) -> str:
    """Fetch a URL and return the raw text content (HTML stripped via regex)."""
    import re
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; OllamaAgent/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # strip tags, collapse whitespace
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:8000]  # cap at 8k chars
    except Exception as exc:
        return f"Error: {exc}"

# ---------------------------------------------------------------------------
# Tool: crawl a site (BFS, up to max_pages)
# ---------------------------------------------------------------------------
def crawl_site(start_url: str, max_pages: int = 5) -> str:
    """Crawl a website starting from start_url, return text from each page."""
    import re
    from urllib.parse import urljoin, urlparse

    visited: set[str] = set()
    queue = [start_url]
    base = urlparse(start_url).netloc
    pages: list[str] = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; OllamaAgent/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            pages.append(f"[{url}] Error: {exc}")
            continue

        # extract links from same domain
        for href in re.findall(r'href=["\']([^"\']+)["\']', raw):
            full = urljoin(url, href)
            if urlparse(full).netloc == base and full not in visited:
                queue.append(full)

        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"[ \t]{2,}", " ", text)
        pages.append(f"=== {url} ===\n{text[:2000]}")

    return "\n\n".join(pages) or "No pages crawled."

# ---------------------------------------------------------------------------
# Tool: spawn a focused subagent for a subtask
# ---------------------------------------------------------------------------
async def spawn_subagent(task: str) -> str:
    """Spawn a subagent with its own context to handle a focused subtask.
    Returns the subagent's final answer."""
    sub = Agent(
        name="Subagent",
        model=OLLAMA_MODEL,
        instructions=(
            "You are a focused subagent. Complete the given task thoroughly "
            "and return a clear, concise result."
        ),
        tools=[run_shell, run_python, scrape_url],
    )
    result = await Runner.run(sub, input=task)
    return result.final_output

# ---------------------------------------------------------------------------
# Build the main agent
# ---------------------------------------------------------------------------
assistant = Agent(
    name="PowerAgent",
    model=OLLAMA_MODEL,
    instructions=(
        "You are a powerful local AI agent running via Ollama. "
        "You can run shell commands, execute Python code, scrape and crawl websites, "
        "and delegate complex subtasks to subagents. "
        "Break hard problems into subtasks and use spawn_subagent for each one. "
        "Always show tool output to the user when relevant."
    ),
    tools=[run_shell, run_python, scrape_url, crawl_site, spawn_subagent],
)

# ---------------------------------------------------------------------------
# Conversation loop
# ---------------------------------------------------------------------------
async def chat():
    print(f"PowerAgent ready  (model: {OLLAMA_MODEL})")
    print("Tools: shell | python | scrape | crawl | subagent")
    print("Type 'quit' to exit.\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        result = await Runner.run(assistant, input=history)

        reply = result.final_output
        history = result.to_input_list()

        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    asyncio.run(chat())
