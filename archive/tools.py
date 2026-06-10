import os
import subprocess
import webbrowser
import random


# -----------------------------
# WALLPAPER TOOLS
# -----------------------------
def set_wallpaper(path):
    try:
        if not os.path.exists(path):
            print(f"[ERROR] File does not exist: {path}")
            return

        full_path = f"file://{path}"

        subprocess.run(
            f"gsettings set org.gnome.desktop.background picture-uri '{full_path}'",
            shell=True
        )

        print(f"[OK] Wallpaper set to: {path}")

    except Exception as e:
        print(f"[ERROR] set_wallpaper: {e}")


def set_random_wallpaper(folder):
    try:
        if not os.path.exists(folder):
            print(f"[ERROR] Folder does not exist: {folder}")
            return

        images = [
            f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".png", ".jpeg"))
        ]

        if not images:
            print("[ERROR] No images found in folder")
            return

        chosen = random.choice(images)
        full_path = os.path.join(folder, chosen)

        set_wallpaper(full_path)

    except Exception as e:
        print(f"[ERROR] set_random_wallpaper: {e}")


def list_images(folder):
    try:
        if not os.path.exists(folder):
            print(f"[ERROR] Folder does not exist: {folder}")
            return []

        return [
            f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".png", ".jpeg"))
        ]

    except Exception as e:
        print(f"[ERROR] list_images: {e}")
        return []


# -----------------------------
# SYSTEM SETTINGS (GNOME)
# -----------------------------
def set_dark_mode():
    try:
        subprocess.run(
            "gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'",
            shell=True
        )
        print("[OK] Dark mode enabled")
    except Exception as e:
        print(f"[ERROR] set_dark_mode: {e}")


def set_light_mode():
    try:
        subprocess.run(
            "gsettings set org.gnome.desktop.interface color-scheme 'default'",
            shell=True
        )
        print("[OK] Light mode enabled")
    except Exception as e:
        print(f"[ERROR] set_light_mode: {e}")


def set_font_size(scale):
    try:
        subprocess.run(
            f"gsettings set org.gnome.desktop.interface text-scaling-factor {scale}",
            shell=True
        )
        print(f"[OK] Font scale set to: {scale}")
    except Exception as e:
        print(f"[ERROR] set_font_size: {e}")


# -----------------------------
# FILE SYSTEM TOOLS
# -----------------------------
def list_files(folder):
    try:
        if not os.path.exists(folder):
            print(f"[ERROR] Folder does not exist: {folder}")
            return []

        return os.listdir(folder)

    except Exception as e:
        print(f"[ERROR] list_files: {e}")
        return []


def empty_trash():
    try:
        subprocess.run("gio trash --empty", shell=True)
        print("[OK] Trash emptied")
    except Exception as e:
        print(f"[ERROR] empty_trash: {e}")


# -----------------------------
# APP / WEB TOOLS
# -----------------------------
def open_app(app_name):
    try:
        subprocess.run(app_name, shell=True)
        print(f"[OK] Opened app: {app_name}")
    except Exception as e:
        print(f"[ERROR] open_app: {e}")


def open_url(url):
    try:
        webbrowser.open(url)
        print(f"[OK] Opened URL: {url}")
    except Exception as e:
        print(f"[ERROR] open_url: {e}")


def open_camera():
    try:
        subprocess.run("cheese", shell=True)
        print("[OK] Camera opened")
    except Exception as e:
        print(f"[ERROR] open_camera: {e}")


# -----------------------------
# ADVANCED (LIMITED SUPPORT)
# -----------------------------
def invert_camera_note():
    print("[INFO] Camera inversion requires OpenCV or app-level implementation")


def keyboard_light_note():
    print("[INFO] Keyboard lighting depends on hardware/driver support")


# -----------------------------
# SAFE COMMAND FALLBACK
# -----------------------------
def run_command(command):
    try:
        subprocess.run(command, shell=True)
        print(f"[OK] Executed: {command}")
    except Exception as e:
        print(f"[ERROR] run_command: {e}")
