import re


# -----------------------------
# SIMPLE COMMAND PLANNER
# -----------------------------
class CommandPlanner:

    def __init__(self):
        # separators for multi-step commands
        self.separators = [" then ", " and ", ","]

    # -----------------------------
    # SPLIT INTO STEPS
    # -----------------------------
    def split_steps(self, text: str) -> list[str]:
        text = text.lower().strip()

        # normalize separators
        for sep in self.separators:
            text = text.replace(sep, "|")

        steps = [s.strip() for s in text.split("|") if s.strip()]
        return steps

    # -----------------------------
    # BASIC PARSE (RULE-BASED)
    # -----------------------------
    def parse_step(self, step: str) -> dict:
        # open app
        if step.startswith("open "):
            return {
                "action": "open_app",
                "params": {"app": step.replace("open ", "", 1)}
            }

        # play media
        if step.startswith("play "):
            return {
                "action": "media_play",
                "params": {"query": step.replace("play ", "", 1)}
            }

        # web search
        if step.startswith("search "):
            return {
                "action": "web_search",
                "params": {"query": step.replace("search ", "", 1)}
            }

        # fallback
        return {
            "action": "unknown",
            "params": {"text": step}
        }

    # -----------------------------
    # PLAN FULL COMMAND
    # -----------------------------
    def plan(self, user_input: str) -> list[dict]:
        steps = self.split_steps(user_input)

        actions = []
        for step in steps:
            action = self.parse_step(step)
            actions.append(action)

        return actions


# -----------------------------
# TEST (optional)
# -----------------------------
if __name__ == "__main__":
    planner = CommandPlanner()

    cmd = "open spotify then play jalwa"
    plan = planner.plan(cmd)

    print("\nPlanned Actions:\n")
    for p in plan:
        print(p)
