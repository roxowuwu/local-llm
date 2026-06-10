import webbrowser
import subprocess
import urllib.parse


# 🌐 Web mappings
WEB_APPS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
}


# ── Helpers ────────────────────────────────────────────────────

def open_website(name: str):
    name = name.lower()

    if name in WEB_APPS:
        webbrowser.open(WEB_APPS[name])
        return True

    return False


def search_google(query: str):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={query_encoded}"
    webbrowser.open(url)


def play_on_youtube(query: str):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    webbrowser.open(url)


def open_app(app_name: str):
    try:
        subprocess.Popen([app_name])
        return True
    except Exception:
        return False


# ── Fast Execution (No Planner) ────────────────────────────────

def fast_execute(action: str, target: str):
    action = (action or "").lower()
    target = (target or "").lower()

    # 🎯 OPEN
    if action == "open":
        if open_website(target):
            print(f"🌐 Opening {target}")
            return

        if open_app(target):
            print(f"🖥️ Launching {target}")
            return

        print(f"⚠️ Could not open {target}")
        return

    # 🔍 SEARCH
    if action == "search":
        print(f"🔍 Searching for {target}")
        search_google(target)
        return

    # ▶️ PLAY
    if action == "play":
        print(f"▶️ Playing {target} on YouTube")
        play_on_youtube(target)
        return

    # ❌ DELETE (placeholder)
    if action == "delete":
        print("⚠️ Delete action not implemented safely.")
        return

    # ⚡ SHUTDOWN
    if action == "shutdown":
        print("⚠️ Shutdown command triggered")
        subprocess.run(["shutdown", "now"])
        return

    print(f"⚠️ Unknown action: {action}")


# ── Plan Execution (Multi-Step) ────────────────────────────────

def execute_plan(plan):
    if not isinstance(plan, list):
        print("⚠️ Invalid plan format.")
        return

    print("🚀 Executing plan...\n")

    for step in plan:
        action = step.get("action")
        target = step.get("target")

        print(f"➡️ {action} → {target}")
        fast_execute(action, target)
