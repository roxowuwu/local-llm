import requests
import json
import subprocess
import re


# -----------------------------
# BUILD PROMPT
# -----------------------------
def build_prompt(user_input: str) -> str:
    return f"""
Convert the following command into JSON.

Only return JSON in this format:
{{
  "action": "string",
  "target": "string"
}}

Command: "{user_input}"
""".strip()


# -----------------------------
# CALL LLM (OLLAMA API)
# -----------------------------
def call_llm(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"].strip()

    except Exception as e:
        print("LLM Error:", e)
        return ""


# -----------------------------
# SAFE JSON PARSE
# -----------------------------
def extract_json(text: str):
    # try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None


# -----------------------------
# EXECUTE ACTION
# -----------------------------
def execute_action(data: dict):
    action = data.get("action")
    target = data.get("target")

    if action == "open":

        if target == "youtube":
            subprocess.run(["xdg-open", "https://youtube.com"])

        elif target == "settings":
            subprocess.run(["gnome-control-center"])

        else:
            print("Unknown target:", target)

    else:
        print("Unknown action:", action)


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    while True:
        user_input = input(">>> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        prompt = build_prompt(user_input)

        output = call_llm(prompt)

        print("\nAI Output:")
        print(output)

        data = extract_json(output)

        if not data:
            print("No valid JSON found")
            continue

        try:
            execute_action(data)
        except Exception as e:
            print("Execution Error:", e)


if __name__ == "__main__":
    main()
