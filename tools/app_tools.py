import json
import subprocess
import os
import shutil

SNAPSHOT_PATH = "config/system_snapshot.json"


# ── Load Snapshot ─────────────────────────────────────────────────────────────────
def _load_snapshot() -> dict:
    if not os.path.exists(SNAPSHOT_PATH):
        raise ValueError("System snapshot not found. Run scanner first.")
    with open(SNAPSHOT_PATH) as f:
        return json.load(f)


# ── Resolve App ───────────────────────────────────────────────────────────────────
def _resolve_app(app_name: str) -> str | None:
    """
    Looks up the real executable for an app name.
    Checks snapshot first (from .desktop files), then falls back to PATH lookup.
    """
    app_name_lower = app_name.lower().strip()

    # 1. Try snapshot (installed_apps from .desktop files)
    try:
        snapshot = _load_snapshot()
        # support both "installed_apps" and "apps" keys
        apps = snapshot.get("installed_apps") or snapshot.get("apps") or []

        for app in apps:
            name = app.get("name", "").lower()
            if app_name_lower in name or name in app_name_lower:
                exec_cmd = app.get("exec", "")
                binary = _clean_exec(exec_cmd)
                if binary:
                    return binary
    except Exception:
        pass

    # 2. Fallback: check if app_name is directly on PATH
    found = shutil.which(app_name_lower)
    if found:
        return found

    # 3. Fallback: common name → binary mappings
    fallback_map = {
        "spotify":          "spotify",
        "telegram":         "telegram-desktop",
        "discord":          "discord",
        "vscode":           "code",
        "vs code":          "code",
        "visual studio code": "code",
        "chrome":           "google-chrome",
        "google chrome":    "google-chrome",
        "firefox":          "firefox",
        "vlc":              "vlc",
        "files":            "nautilus",
        "file manager":     "nautilus",
        "terminal":         "gnome-terminal",
        "calculator":       "gnome-calculator",
        "settings":         "gnome-control-center",
    }
    binary = fallback_map.get(app_name_lower)
    if binary and shutil.which(binary):
        return binary

    return None


# ── Clean Exec String ─────────────────────────────────────────────────────────────
def _clean_exec(exec_str: str) -> str:
    """
    .desktop Exec fields look like: 'spotify %U' or '/usr/bin/app --flag %F'
    Strip %U, %F, %u, %f, %i, %c, %k placeholders before running.
    """
    if not exec_str:
        return ""
    import re
    cleaned = re.sub(r'%[a-zA-Z]', '', exec_str).strip()
    # return just the binary (first token)
    parts = cleaned.split()
    return parts[0] if parts else ""


# ── Open App ──────────────────────────────────────────────────────────────────────
def open_app(params: dict, prefs: dict) -> str:
    app_name = params.get("app_name") or params.get("app") or params.get("name")
    if not app_name:
        raise ValueError("No app name provided")

    binary = _resolve_app(app_name)
    if not binary:
        raise ValueError(f"App not found: '{app_name}' — is it installed?")

    try:
        subprocess.Popen(
            [binary],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Opened: {app_name}"
    except FileNotFoundError:
        raise ValueError(f"Binary not found: '{binary}'")
    except Exception as e:
        raise ValueError(f"Failed to open {app_name}: {e}")


# ── Close App ─────────────────────────────────────────────────────────────────────
def close_app(params: dict, prefs: dict) -> str:
    app_name = params.get("app_name") or params.get("app") or params.get("name")
    if not app_name:
        raise ValueError("No app name provided")

    result = subprocess.run(
        ["pkill", "-fi", app_name],   # -i = case insensitive, -f = match full cmd
        capture_output=True,
    )
    if result.returncode == 0:
        return f"Closed: {app_name}"
    return f"Not running: {app_name}"


# ── List Apps ─────────────────────────────────────────────────────────────────────
def list_apps(params: dict, prefs: dict) -> str:
    snapshot = _load_snapshot()
    apps = snapshot.get("installed_apps") or snapshot.get("apps") or []

    if not apps:
        return "No apps found in snapshot."

    print("\nInstalled Apps:\n")
    for i, app in enumerate(apps[:30], 1):
        name = app.get("name", "unknown")
        binary = _clean_exec(app.get("exec", ""))
        print(f"  {i:2}. {name:<30} ({binary})")

    return f"Listed {min(30, len(apps))} of {len(apps)} installed apps"
