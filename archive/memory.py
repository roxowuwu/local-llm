import json
import os

MEMORY_FILE = "memory.json"


# ── Load Memory ────────────────────────────────────────────────
def load_memory():
    """
    Load memory safely from file.
    If file doesn't exist or is corrupted → return empty memory.
    """
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        # corrupted file → reset
        return {}


# ── Save Memory ────────────────────────────────────────────────
def save_memory(memory: dict):
    """
    Save memory safely to file.
    """
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save memory: {e}")
