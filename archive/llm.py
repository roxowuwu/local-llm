import subprocess
import json

# ⚙️ Change model if needed
MODEL = "llama3"   # or "mistral", "phi", "tinyllama"


# ── Core Ollama Call ───────────────────────────────────────────
def call_ollama(prompt: str):
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        output = result.stdout.decode().strip()
        return output

    except Exception as e:
        return f"Error: {e}"


# ── Chat (Normal AI Response) ──────────────────────────────────
def ask_llm(prompt: str):
    return call_ollama(prompt)


# ── Intent Classification ──────────────────────────────────────
def classify_with_llm(user_input: str):
    prompt = f"""
Classify the user input into JSON.

Return ONLY JSON in this format:
{{
  "intent": "chat" or "action",
  "action": "...",
  "target": "...",
  "complexity": "simple" or "complex"
}}

Rules:
- If it's a question → chat
- If it's asking to do something → action
- If multiple steps → complex
- Otherwise → simple

Input: "{user_input}"
Output:
""".strip()

    response = call_ollama(prompt)

    # 🛡️ Try parsing JSON safely
    try:
        # Extract JSON part if model adds extra text
        start = response.find("{")
        end = response.rfind("}") + 1
        json_str = response[start:end]

        data = json.loads(json_str)
        return data

    except Exception:
        # fallback safe default
        return {
            "intent": "chat",
            "confidence": 0.5
        }
