"""
Ollama Agent — OpenAI Agents SDK + Ollama (OpenAI-compatible API)

Ollama exposes an OpenAI-compatible REST API at http://localhost:11434/v1
The openai-agents SDK routes through the standard openai client,
so we just swap the base_url and provide a dummy api_key.

Setup:
  1. Install Ollama on your Windows machine: https://ollama.com/download
  2. Pull a model:  ollama pull llama3.2
  3. Run Ollama:    ollama serve  (or it starts automatically)
  4. Install deps:  pip install -r requirements.txt
  5. Run:          python agent.py
"""

import asyncio
from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3.2"          # change to whichever model you pulled
OLLAMA_API_KEY = "ollama"          # Ollama ignores this; SDK requires a value

# ---------------------------------------------------------------------------
# Point the SDK at Ollama
# ---------------------------------------------------------------------------
ollama_client = AsyncOpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key=OLLAMA_API_KEY,
)
set_default_openai_client(ollama_client)

# ---------------------------------------------------------------------------
# Define tools the agent can call
# ---------------------------------------------------------------------------
def get_weather(city: str) -> str:
    """Return a mock weather report for the given city."""
    # Replace with a real weather API call if desired
    return f"The weather in {city} is sunny, 22°C with light winds."

def calculate(expression: str) -> str:
    """Safely evaluate a basic math expression and return the result."""
    allowed = set("0123456789+-*/()., ")
    if not all(c in allowed for c in expression):
        return "Error: only basic arithmetic is supported."
    try:
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"

# ---------------------------------------------------------------------------
# Build the agent
# ---------------------------------------------------------------------------
assistant = Agent(
    name="OllamaAssistant",
    model=OLLAMA_MODEL,
    instructions=(
        "You are a helpful assistant running fully locally via Ollama. "
        "You have access to a weather tool and a calculator. "
        "Use them when the user's request requires it."
    ),
    tools=[get_weather, calculate],
)

# ---------------------------------------------------------------------------
# Run a simple conversation loop
# ---------------------------------------------------------------------------
async def chat():
    print(f"Ollama Agent ready  (model: {OLLAMA_MODEL})")
    print("Type 'quit' to exit.\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        result = await Runner.run(
            assistant,
            input=history,
        )

        reply = result.final_output
        history = result.to_input_list()   # keep full conversation context

        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    asyncio.run(chat())
