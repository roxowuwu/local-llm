import subprocess
import yaml
import logging


def load_config():
    try:
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load config.yaml: {e}")
        return None


def execute(data):
    try:
        config = load_config()

        if not config:
            logging.error("Config not loaded")
            return

        BLOCKED = config.get("blocked_keywords", [])
        SENSITIVE = config.get("sensitive_keywords", [])
        PLUGINS = config.get("plugins", {})

        if data.get("action") == "run":
            command = data.get("command")

            if not command:
                logging.error("No command provided")
                return

            command_lower = command.lower()

            logging.info(f"AI Command: {command}")

            # 🚫 Block OS-level operations
            for word in BLOCKED:
                if word in command_lower:
                    logging.warning("Blocked: OS-level modification not allowed")
                    return

            # ⚠️ Sensitive commands
            for word in SENSITIVE:
                if word in command_lower:
                    confirm = input(
                        f"Sensitive action detected: '{command}'. Proceed? (y/n): "
                    )
                    if confirm.lower() != "y":
                        logging.info("Command cancelled")
                        return
                    break

            # 🧠 Extra delete protection
            if "rm" in command_lower:
                confirm = input(
                    f"Delete operation detected: '{command}'. Are you sure? (y/n): "
                )
                if confirm.lower() != "y":
                    logging.info("Delete cancelled")
                    return

            logging.info(f"Executing: {command}")
            subprocess.run(command, shell=True)

    except Exception as e:
        logging.error(f"Execution Error: {e}")
