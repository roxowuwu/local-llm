class ShortTermMemory:

    def __init__(self, max_turns: int = 10):
        self.history = []
        self.max_turns = max_turns

    # -----------------------------
    # ADD MESSAGE
    # -----------------------------
    def add(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content
        })

        # trim history (2 entries per turn: user + assistant)
        max_entries = self.max_turns * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]

    # -----------------------------
    # FORMAT FOR PROMPT
    # -----------------------------
    def format_for_prompt(self) -> str:
        if not self.history:
            return "No previous conversation."

        recent = self.history[-6:]

        lines = []
        for item in recent:
            role = item["role"].capitalize()
            content = item["content"]
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    # -----------------------------
    # GET ALL
    # -----------------------------
    def get_all(self) -> list:
        return self.history

    # -----------------------------
    # CLEAR MEMORY
    # -----------------------------
    def clear(self):
        self.history = []
