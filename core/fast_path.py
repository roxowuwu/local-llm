import re
import yaml


class FastPathEngine:

    def __init__(self, rules_path: str = "config/rules.yaml"):
        self.rules = []
        self._load(rules_path)

    # ── Load + Compile Rules ──────────────────────────────────────────────────────
    def _load(self, rules_path: str):
        try:
            with open(rules_path) as f:
                raw = yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"[WARN] rules.yaml not found at {rules_path} — fast path disabled.")
            return

        for rule in raw.get("rules", []):
            action  = rule.get("action")
            matches = rule.get("match", [])
            extra   = {k: v for k, v in rule.items() if k not in ("action", "match")}

            if not action or not matches:
                continue

            patterns = []
            for phrase in matches:
                patterns.append({
                    "raw":      phrase.lower(),
                    "has_param": "{" in phrase,
                    "regex":    self._to_regex(phrase),
                })

            self.rules.append({
                "action":   action,
                "patterns": patterns,
                "extra":    extra,
            })

    # ── Pattern → Regex ───────────────────────────────────────────────────────────
    def _to_regex(self, phrase: str) -> re.Pattern:
        """
        Converts a rule phrase into a compiled regex.
        {query} → named capture group (?P<query>.+)
        Everything else is escaped.
        """
        escaped = re.escape(phrase.lower())
        # turn escaped \{param\} back into named group
        escaped = re.sub(r"\\\{(\w+)\\\}", r"(?P<\1>.+)", escaped)
        return re.compile(f"^{escaped}$", re.IGNORECASE)

    # ── Match ─────────────────────────────────────────────────────────────────────
    def match(self, user_input: str) -> dict | None:
        text = user_input.lower().strip()

        # Pass 1 — exact match (fastest, no regex needed)
        for rule in self.rules:
            for p in rule["patterns"]:
                if not p["has_param"] and text == p["raw"]:
                    return self._build(rule, {})

        # Pass 2 — partial/fuzzy match for non-param rules
        # e.g. "can you open youtube please" still matches "open youtube"
        for rule in self.rules:
            for p in rule["patterns"]:
                if not p["has_param"] and p["raw"] in text:
                    return self._build(rule, {})

        # Pass 3 — parameterized match (regex)
        for rule in self.rules:
            for p in rule["patterns"]:
                if p["has_param"]:
                    m = p["regex"].match(text)
                    if m:
                        return self._build(rule, m.groupdict())

        return None

    # ── Build Result ──────────────────────────────────────────────────────────────
    def _build(self, rule: dict, captured_params: dict) -> dict:
        """
        Merges extra fields (app_name, url, source etc) into BOTH
        top-level and params so tools can find them either way.
        """
        # extra fields from yaml (e.g. app_name, url) + regex captures
        merged_params = {**rule["extra"], **captured_params}

        result = {
            "type":   "action",
            "action": rule["action"],
            "params": merged_params,
        }

        # also set extra fields at top level for tools that read directly
        result.update(rule["extra"])

        return result
