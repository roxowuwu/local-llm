import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "history": [],
            "last_action": None
        }

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# STORE DATA
# -----------------------------
def store_interaction(user_input, response):
    memory = load_memory()

    memory["history"].append({
        "user": user_input,
        "response": response
    })

    # keep last 20 interactions only
    memory["history"] = memory["history"][-20:]

    save_memory(memory)


def store_action(action_data):
    memory = load_memory()
    memory["last_action"] = action_data
    save_memory(memory)


# -----------------------------
# RETRIEVE DATA
# -----------------------------
def get_last_action():
    memory = load_memory()
    return memory.get("last_action")


def get_history():
    memory = load_memory()
    return memory.get("history", [])
