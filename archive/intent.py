import re

# ⚡ Strong action keywords (high confidence)
ACTION_KEYWORDS = {
    "open": "open",
    "launch": "open",
    "start": "open",
    "play": "play",
    "search": "search",
    "find": "search",
    "delete": "delete",
    "remove": "delete",
    "shutdown": "shutdown",
    "restart": "restart"
}

# 🧠 Soft hints (natural language / Hindi / casual)
SOFT_ACTION_HINTS = [
    "laga", "chala", "play", "run", "dekh", "sun", "dikha", "start",
    "show", "open", "launch"
]

# 💬 Question words
QUESTION_WORDS = [
    "what", "why", "how", "when", "where", "who",
    "explain", "define", "tell", "meaning"
]

# 🌐 Known platforms
KNOWN_TARGETS = [
    "youtube", "google", "gmail", "spotify", "chrome", "firefox"
]


# ── Utility functions ──────────────────────────────────────────

def extract_target(text: str):
    """
    Try to extract meaningful target (song, app, query)
    """
    text = text.lower()

    # remove known verbs
    cleaned = re.sub(r"(open|play|search|find|run|start)", "", text)

    return cleaned.strip() or text


def detect_complexity(text: str):
    """
    Detect if command is complex (multi-step)
    """
    if " and " in text or " then " in text:
        return "complex"
    return "simple"


# ── Main Intent Detection ──────────────────────────────────────

def detect_intent(text: str):
    text = text.lower().strip()

    # 🔁 Repeat detection (handled early)
    if text in ["repeat", "again", "do it again"]:
        return {"intent": "repeat"}

    # ⚡ LEVEL 1 — Strong keyword detection
    for word, action in ACTION_KEYWORDS.items():
        if word in text:
            return {
                "intent": "action",
                "action": action,
                "target": extract_target(text),
                "complexity": detect_complexity(text),
                "confidence": 0.95
            }

    # 🧠 LEVEL 2 — Soft hint detection
    if any(hint in text for hint in SOFT_ACTION_HINTS):
        return {
            "intent": "action",
            "action": "play",  # default assumption
            "target": extract_target(text),
            "complexity": detect_complexity(text),
            "confidence": 0.7
        }

    # 💬 LEVEL 3 — Question detection
    if any(q in text for q in QUESTION_WORDS) or text.endswith("?"):
        return {
            "intent": "chat",
            "confidence": 0.9
        }

    # 🌐 LEVEL 4 — Known targets (like "youtube kholo")
    for target in KNOWN_TARGETS:
        if target in text:
            return {
                "intent": "action",
                "action": "open",
                "target": target,
                "complexity": "simple",
                "confidence": 0.8
            }

    # ❓ Unknown → fallback
    return {
        "intent": "unknown",
        "confidence": 0.0
    }
