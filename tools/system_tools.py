import subprocess
import os
import random
from pathlib import Path
import json

SNAPSHOT_PATH = "config/system_snapshot.json"


# -----------------------------
# DARK MODE
# -----------------------------
def set_dark_mode(params, prefs):
    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.interface",
        "color-scheme", "prefer-dark"
    ])
    return "Dark mode enabled"


# -----------------------------
# LIGHT MODE
# -----------------------------
def set_light_mode(params, prefs):
    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.interface",
        "color-scheme", "default"
    ])
    return "Light mode enabled"


# -----------------------------
# SET WALLPAPER
# -----------------------------
def set_wallpaper(params, prefs):
    path = params.get("path")

    if not path:
        raise ValueError("No wallpaper path provided")

    if not os.path.exists(path):
        raise ValueError(f"File not found: {path}")

    uri = f"file://{path}"

    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.background",
        "picture-uri", uri
    ])

    return f"Wallpaper set to: {path}"


# -----------------------------
# RANDOM WALLPAPER
# -----------------------------
def set_random_wallpaper(params, prefs):
    folder = params.get("folder")

    if not folder or not os.path.isdir(folder):
        raise ValueError("Invalid folder")

    images = [
        f for f in Path(folder).iterdir()
        if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    ]

    if not images:
        raise ValueError("No images found in folder")

    chosen = random.choice(images)

    return set_wallpaper({"path": str(chosen)}, prefs)


# -----------------------------
# FONT SIZE
# -----------------------------
def set_font_size(params, prefs):
    scale = params.get("scale")

    if scale is None:
        raise ValueError("No scale provided")

    scale = float(scale)

    if not (0.5 <= scale <= 3.0):
        raise ValueError("Scale must be between 0.5 and 3.0")

    subprocess.run([
        "gsettings", "set",
        "org.gnome.desktop.interface",
        "text-scaling-factor", str(scale)
    ])

    return f"Font scale set to: {scale}"


# -----------------------------
# BRIGHTNESS
# -----------------------------
def set_brightness(params, prefs):
    level = params.get("level")

    if level is None:
        raise ValueError("No brightness level provided")

    level = int(level)
    level = max(0, min(100, level))

    subprocess.run(["brightnessctl", "set", f"{level}%"])

    return f"Brightness set to {level}%"


# -----------------------------
# EMPTY TRASH
# -----------------------------
def empty_trash(params, prefs):
    subprocess.run(["gio", "trash", "--empty"])
    return "Trash emptied"


# -----------------------------
# SYSTEM INFO
# -----------------------------
def get_system_info(params, prefs):
    if not os.path.exists(SNAPSHOT_PATH):
        return "System snapshot not found"

    with open(SNAPSHOT_PATH, "r") as f:
        data = json.load(f)

    system = data.get("system", {})
    storage = data.get("storage", {})

    print("\nSystem Info:\n")
    print(f"OS: {system.get('os')}")
    print(f"Hostname: {system.get('hostname')}")
    print(f"Kernel: {system.get('kernel')}")
    print(f"Storage: {storage.get('used_gb')}GB used / {storage.get('total_gb')}GB")

    return "System info displayed"
