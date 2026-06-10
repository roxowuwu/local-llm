import sys

# ⚠️ Sensitive actions list
SENSITIVE_ACTIONS = [
    "delete",
    "remove",
    "shutdown",
    "restart",
    "format",
]


# ── Check if action is sensitive ───────────────────────────────
def is_sensitive(action: str) -> bool:
    if not action:
        return False
    return action.lower() in SENSITIVE_ACTIONS


# ── Ask user for confirmation ──────────────────────────────────
def confirm_action(user_input: str) -> bool:
    """
    Ask user before executing dangerous commands
    """
    print(f"\n⚠️ WARNING: This action may be dangerous!")
    print(f"👉 {user_input}")

    while True:
        choice = input("Confirm? (yes/no): ").strip().lower()

        if choice in ["yes", "y"]:
            return True
        elif choice in ["no", "n"]:
            return False
        else:
            print("Please type 'yes' or 'no'")
