import json
import re
import subprocess


class LLMBrain:
    def __init__(self, system_context: str, prefs=None, model="llama3"):
        self.system_context = system_context
        self.prefs = prefs
        self.model = model

    # ── Main Resolve ──────────────────────────────────────────────────────────────
    def resolve(self, user_input: str, intent_hint: dict, history: str) -> dict | None:
        prompt = self._build_prompt(user_input, intent_hint, history)
        response = self._call_llm(prompt)
        data = self._safe_parse(response)

        if data and self._validate_response(data):
            return data

        # Retry with stricter instruction
        strict_prompt = prompt + "\n\nRETURN ONLY THE JSON OBJECT. NO OTHER TEXT."
        response = self._call_llm(strict_prompt)
        data = self._safe_parse(response)

        if data and self._validate_response(data):
            return data

        return None

    # ── Prompt Builder ────────────────────────────────────────────────────────────
    def _build_prompt(self, user_input: str, intent_hint: dict, history: str) -> str:
        return f"""
{self.system_context}

CONVERSATION HISTORY:
{history if history else "None"}

INTENT HINT:
category={intent_hint.get("category", "unknown")}

USER INPUT:
{user_input}

You are a Linux desktop assistant. Return ONLY a JSON object — no explanation, no markdown, no extra text.

If the user is chatting or asking a question, return:
{{"type": "chat", "message": "your reply here"}}

If the user wants to DO something (open app, play music, change settings etc), return:
{{"type": "action", "action": "action_name", "params": {{}}}}

If you need more info before acting, return:
{{"type": "clarify", "question": "your question here"}}

Valid action names:
open_app, close_app, open_url, web_search,
media_play, media_pause, media_skip, media_volume,
set_dark_mode, set_light_mode, set_wallpaper, set_random_wallpaper,
set_font_size, set_brightness, empty_trash, get_system_info,
read_file, write_file, find_file,
storage_report, find_large_files, find_duplicate_files

RETURN ONLY JSON:
""".strip()

    # ── Call LLM (Ollama) ─────────────────────────────────────────────────────────
    def _call_llm(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            return result.stdout.decode().strip()
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""

    # ── Safe JSON Parse ───────────────────────────────────────────────────────────
    def _safe_parse(self, text: str) -> dict | None:
        """
        Extracts JSON even if the LLM adds text around it.
        Tries full parse first, then looks for {...} block inside the response.
        """
        if not text:
            return None

        # Try parsing the full response first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find the first { ... } block in the response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None

    # ── Validate Response ─────────────────────────────────────────────────────────
    def _validate_response(self, data: dict) -> bool:
        if not isinstance(data, dict):
            return False

        t = data.get("type")

        if t == "chat":
            return bool(data.get("message"))

        if t == "clarify":
            return bool(data.get("question"))

        if t == "action":
            return (
                bool(data.get("action")) and
                isinstance(data.get("params", {}), dict)
            )

        # If no type field but has action — accept it and patch it
        if "action" in data:
            data["type"] = "action"
            if "params" not in data:
                data["params"] = {}
            return True

        return False
