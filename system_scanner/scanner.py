import os
import json
import time
import socket
import subprocess
from pathlib import Path
from difflib import get_close_matches

SNAPSHOT_PATH = "config/system_snapshot.json"
CACHE_TTL = 3600  # 1 hour


class SystemScanner:

    def __init__(self, apps_dir="/usr/share/applications", home_dir=None):
        self.apps_dir = apps_dir
        self.home_dir = home_dir or str(Path.home())
        self.snapshot = {}

    # -----------------------------
    # MAIN SCAN
    # -----------------------------
    def scan(self):
        if self._is_cache_valid():
            self._load_cache()
            return self.snapshot

        apps = self._scan_apps()
        os_info = self._get_os_info()
        storage = self._get_storage()
        home_size = self._get_home_size()
        top_dirs = self._get_top_dirs()

        self.snapshot = {
            "timestamp": int(time.time()),
            "os": os_info,
            "hostname": socket.gethostname(),
            "installed_apps": apps,
            "storage_summary": storage,
            "home_size": home_size,
            "top_space_users": top_dirs,
            "config_locations": {
                "home": self.home_dir,
                "apps_dir": self.apps_dir
            }
        }

        self._save_cache()
        return self.snapshot

    # -----------------------------
    # CACHE HANDLING
    # -----------------------------
    def _is_cache_valid(self):
        if not os.path.exists(SNAPSHOT_PATH):
            return False

        with open(SNAPSHOT_PATH, "r") as f:
            data = json.load(f)

        ts = data.get("timestamp", 0)
        return (time.time() - ts) < CACHE_TTL

    def _load_cache(self):
        with open(SNAPSHOT_PATH, "r") as f:
            self.snapshot = json.load(f)

    def _save_cache(self):
        os.makedirs("config", exist_ok=True)
        with open(SNAPSHOT_PATH, "w") as f:
            json.dump(self.snapshot, f, indent=4)

    # -----------------------------
    # APP SCAN
    # -----------------------------
    def _scan_apps(self):
        apps = []

        if not os.path.exists(self.apps_dir):
            return apps

        for file in os.listdir(self.apps_dir):
            if file.endswith(".desktop"):
                path = os.path.join(self.apps_dir, file)
                name, exec_cmd = self._parse_desktop(path)

                if name and exec_cmd:
                    apps.append({
                        "name": name.lower(),
                        "exec": exec_cmd
                    })

        return apps

    def _parse_desktop(self, path):
        name = None
        exec_cmd = None

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("Name="):
                        name = line.split("=", 1)[1].strip()
                    elif line.startswith("Exec="):
                        exec_cmd = line.split("=", 1)[1].strip().split()[0]
        except:
            pass

        return name, exec_cmd

    # -----------------------------
    # OS INFO
    # -----------------------------
    def _get_os_info(self):
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        return line.split("=")[1].replace('"', '').strip()
        except:
            return "Unknown OS"

    # -----------------------------
    # STORAGE
    # -----------------------------
    def _get_storage(self):
        try:
            output = subprocess.check_output(["df", "-h", "/"]).decode().splitlines()[1]
            parts = output.split()
            return {
                "total": parts[1],
                "used": parts[2],
                "free": parts[3],
                "usage": parts[4]
            }
        except:
            return {}

    def _get_home_size(self):
        try:
            output = subprocess.check_output(["du", "-sh", self.home_dir]).decode()
            return output.split()[0]
        except:
            return "Unknown"

    # -----------------------------
    # TOP SPACE USERS
    # -----------------------------
    def _get_top_dirs(self):
        try:
            output = subprocess.check_output(
                ["du", "-h", "--max-depth=1", self.home_dir]
            ).decode().splitlines()

            sizes = []
            for line in output:
                size, path = line.split("\t")
                sizes.append((size, path))

            return sorted(sizes, reverse=True)[:10]
        except:
            return []

    # -----------------------------
    # PUBLIC API
    # -----------------------------
    def get_context_snapshot(self):
        return self.scan()

    def resolve_app(self, name: str):
        apps = self.scan().get("installed_apps", [])

        names = [app["name"] for app in apps]
        match = get_close_matches(name.lower(), names, n=1, cutoff=0.5)

        if match:
            for app in apps:
                if app["name"] == match[0]:
                    return app["exec"]

        return None
