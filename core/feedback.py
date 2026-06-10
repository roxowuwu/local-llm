class FeedbackLayer:

    def __init__(self):
        # track failures per action (simple memory)
        self.failure_count = {}

        # define action types
        self.retryable_actions = {"open_url", "media_play"}
        self.destructive_actions = {
            "delete_file",
            "shutdown",
            "empty_trash",
            "change_system_setting"
        }

    # -----------------------------
    # MAIN EVALUATE
    # -----------------------------
    def evaluate(self, action_data, success, result_msg, user_input) -> dict:
        action = action_data.get("action", "unknown")

        # success case
        if success:
            self._reset_failure(action)
            return {
                "retry": False,
                "ask_user": None,
                "log_failure": False
            }

        # failure case
        self._increment_failure(action)
        fail_count = self.failure_count.get(action, 1)

        # retryable actions
        if action in self.retryable_actions and fail_count == 1:
            return {
                "retry": True,
                "ask_user": None,
                "log_failure": False
            }

        # destructive actions
        if action in self.destructive_actions:
            return {
                "retry": False,
                "ask_user": "Should I try differently?",
                "log_failure": True if fail_count >= 2 else False
            }

        # general failure (non-retryable)
        if fail_count >= 2:
            return {
                "retry": False,
                "ask_user": "Something went wrong. Try another way?",
                "log_failure": True
            }

        # default fallback
        return {
            "retry": False,
            "ask_user": None,
            "log_failure": False
        }

    # -----------------------------
    # HELPERS
    # -----------------------------
    def _increment_failure(self, action):
        self.failure_count[action] = self.failure_count.get(action, 0) + 1

    def _reset_failure(self, action):
        if action in self.failure_count:
            del self.failure_count[action]
