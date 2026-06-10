import sys
import json
import logging
import subprocess
import re
import shutil
import sqlite3
import webbrowser
import yaml
from datetime import datetime
from pathlib import Path


# ── Logging ───────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("assistant")


# ── Config ────────────────────────────────────────────────────────────────────────
def load_prefs() -> dict:
    path = Path("config/user_prefs.yaml")
    if not path.exists():
        return {
            "music_app": "spotify",
            "browser": "firefox",
            "model": "llama3",
            "home_dir": str(Path.home()),
            "apps_dir": "/usr/share/applications",
        }
    with open(path) as f:
        return yaml.safe_load(f) or {}


# ── App Resolver ──────────────────────────────────────────────────────────────────
class AppResolver:
    """
    Builds a name → binary map from .desktop files at startup.
    Lets us open ANY installed app by name.
    """

    COMMON = {
        "telegram":           "telegram-desktop",
        "vs code":            "code",
        "vscode":             "code",
        "chrome":             "google-chrome",
        "google chrome":      "google-chrome",
        "file manager":       "nautilus",
        "files":              "nautilus",
        "terminal":           "gnome-terminal",
        "calculator":         "gnome-calculator",
        "settings":           "gnome-control-center",
        "text editor":        "gedit",
        "music":              "rhythmbox",
    }

    def __init__(self, apps_dir: str):
        self.apps_dir = Path(apps_dir)
        self._map: dict[str, str] = {}
        self._build()

    def _build(self):
        """Read all .desktop files and build name → binary map."""
        if not self.apps_dir.exists():
            log.warning(f"apps_dir not found: {self.apps_dir}")
            return

        for desktop in self.apps_dir.glob("*.desktop"):
            try:
                name, exec_cmd = None, None
                with open(desktop, errors="ignore") as f:
                    for line in f:
                        if line.startswith("Name=") and name is None:
                            name = line.split("=", 1)[1].strip().lower()
                        if line.startswith("Exec=") and exec_cmd is None:
                            raw = line.split("=", 1)[1].strip()
                            # strip %U %F etc
                            raw = re.sub(r'%\w', '', raw).strip()
                            exec_cmd = raw.split()[0]
                if name and exec_cmd:
                    self._map[name] = exec_cmd
                    # also index by filename stem
                    self._map[desktop.stem.lower()] = exec_cmd
            except Exception:
                continue

        log.info(f"AppResolver: indexed {len(self._map)} apps")

    def resolve(self, name: str) -> str | None:
        name = name.lower().strip()

        # 1. exact map match
        if name in self._map:
            return self._map[name]

        # 2. partial map match
        for key, binary in self._map.items():
            if name in key or key in name:
                return binary

        # 3. common name fallback
        binary = self.COMMON.get(name)
        if binary:
            return binary

        # 4. direct PATH lookup
        found = shutil.which(name)
        if found:
            return found

        return None


# ── Memory ────────────────────────────────────────────────────────────────────────
class Memory:
    """SQLite-backed memory. Stores interactions and last action."""

    def __init__(self, db_path: str = "memory/memory.db"):
        Path(db_path).parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init()
        self.history: list[dict] = []  # in-session short term

    def _init(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                user      TEXT,
                assistant TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                ts   TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    def add(self, user: str, assistant: str):
        self.history.append({"user": user, "assistant": assistant})
        if len(self.history) > 10:
            self.history = self.history[-10:]
        self.conn.execute(
            "INSERT INTO interactions (ts, user, assistant) VALUES (?,?,?)",
            (datetime.now().isoformat(), user, assistant)
        )
        self.conn.commit()

    def save_action(self, action: dict):
        self.conn.execute(
            "INSERT INTO actions (ts, data) VALUES (?,?)",
            (datetime.now().isoformat(), json.dumps(action))
        )
        self.conn.commit()

    def last_action(self) -> dict | None:
        row = self.conn.execute(
            "SELECT data FROM actions ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return json.loads(row[0]) if row else None

    def format_history(self) -> str:
        if not self.history:
            return "No previous conversation."
        lines = []
        for h in self.history[-4:]:
            lines.append(f"User: {h['user']}")
            lines.append(f"Assistant: {h['assistant']}")
        return "\n".join(lines)


# ── LLM ───────────────────────────────────────────────────────────────────────────
class LLM:
    def __init__(self, model: str, system_context: str):
        self.model = model
        self.system_context = system_context

    def ask(self, user_input: str, history: str) -> dict | None:
        prompt = f"""
{self.system_context}

CONVERSATION HISTORY:
{history}

USER: {user_input}

You are a Linux desktop assistant. Return ONLY a JSON object.

For chat/questions:
{{"type": "chat", "message": "your reply"}}

For opening an app:
{{"type": "action", "action": "open_app", "app_name": "exact app name"}}

For opening a URL:
{{"type": "action", "action": "open_url", "url": "https://..."}}

For playing music:
{{"type": "action", "action": "media_play", "query": "song or artist name"}}

For web search:
{{"type": "action", "action": "web_search", "query": "search terms"}}

For fetching info from a website:
{{"type": "action", "action": "web_fetch", "url": "https://...", "question": "what to look for"}}

For system info:
{{"type": "action", "action": "system_info"}}

RETURN ONLY JSON. NO explanation. NO markdown.
""".strip()

        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            raw = result.stdout.decode().strip()
            return self._parse(raw)
        except subprocess.TimeoutExpired:
            log.error("LLM timed out")
            return None
        except Exception as e:
            log.error(f"LLM error: {e}")
            return None

    def _parse(self, text: str) -> dict | None:
        if not text:
            return None
        # try full parse
        try:
            return json.loads(text)
        except Exception:
            pass
        # extract first {...} block
        m = re.search(r'\{.*?\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
        return None


# ── Executor ──────────────────────────────────────────────────────────────────────
class Executor:
    def __init__(self, prefs: dict, resolver: AppResolver):
        self.prefs    = prefs
        self.resolver = resolver
        self.browser  = prefs.get("browser", "firefox")

    def run(self, action: dict) -> tuple[bool, str]:
        name = action.get("action", "")
        try:
            if name == "open_app":
                return self._open_app(action)
            elif name == "open_url":
                return self._open_url(action)
            elif name == "web_search":
                return self._web_search(action)
            elif name == "web_fetch":
                return self._web_fetch(action)
            elif name == "media_play":
                return self._media_play(action)
            elif name == "media_pause":
                return self._media_pause()
            elif name == "media_skip":
                return self._media_skip()
            elif name == "system_info":
                return self._system_info()
            elif name == "empty_trash":
                return self._empty_trash()
            elif name == "set_dark_mode":
                return self._dark_mode(True)
            elif name == "set_light_mode":
                return self._dark_mode(False)
            else:
                return False, f"Unknown action: '{name}'"
        except Exception as e:
            log.error(f"Executor error in {name}: {e}")
            return False, f"Error: {e}"

    def _open_app(self, action: dict) -> tuple[bool, str]:
        app_name = (
            action.get("app_name") or
            action.get("params", {}).get("app_name") or
            action.get("params", {}).get("app")
        )
        if not app_name:
            return False, "No app name provided"

        binary = self.resolver.resolve(app_name)
        if not binary:
            return False, f"App not found: '{app_name}'"

        subprocess.Popen(
            [binary],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, f"Opened: {app_name}"

    def _open_url(self, action: dict) -> tuple[bool, str]:
        url = action.get("url") or action.get("params", {}).get("url")
        if not url:
            return False, "No URL provided"
        if not url.startswith("http"):
            url = "https://" + url

        browser = self.resolver.resolve(self.browser)
        if browser:
            subprocess.Popen(
                [browser, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            webbrowser.open(url)
        return True, f"Opened: {url}"

    def _web_search(self, action: dict) -> tuple[bool, str]:
        query = action.get("query") or action.get("params", {}).get("query", "")
        engine = self.prefs.get("preferred_search", "google")
        engines = {
            "google": "https://google.com/search?q=",
            "bing":   "https://bing.com/search?q=",
            "ddg":    "https://duckduckgo.com/?q=",
        }
        base = engines.get(engine, engines["google"])
        url  = base + query.replace(" ", "+")
        return self._open_url({"url": url})

    def _web_fetch(self, action: dict) -> tuple[bool, str]:
        """Fetch text content from a URL and return relevant info."""
        url      = action.get("url", "")
        question = action.get("question", "")
        if not url:
            return False, "No URL to fetch"
        try:
            import urllib.request
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode(errors="ignore")
            # strip tags
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            # trim to 3000 chars for LLM
            snippet = text[:3000]
            print(f"\nPage content (for: {question}):\n{snippet}\n")
            return True, f"Fetched content from {url}"
        except Exception as e:
            return False, f"Could not fetch {url}: {e}"

    def _media_play(self, action: dict) -> tuple[bool, str]:
        query    = action.get("query") or action.get("params", {}).get("query", "")
        music_app = self.prefs.get("music_app", "spotify")

        if music_app == "spotify":
            # try playerctl first (if spotify is open)
            if shutil.which("playerctl"):
                subprocess.run(["playerctl", "play"], capture_output=True)
            # open spotify with search URI
            uri = f"spotify:search:{query.replace(' ', '%20')}"
            subprocess.Popen(
                ["spotify", "--uri", uri],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, f"Playing on Spotify: {query}"

        # fallback: youtube search
        return self._web_search({"query": query + " official audio"})

    def _media_pause(self) -> tuple[bool, str]:
        if shutil.which("playerctl"):
            subprocess.run(["playerctl", "pause"], capture_output=True)
            return True, "Paused"
        return False, "playerctl not found — install with: sudo apt install playerctl"

    def _media_skip(self) -> tuple[bool, str]:
        if shutil.which("playerctl"):
            subprocess.run(["playerctl", "next"], capture_output=True)
            return True, "Skipped"
        return False, "playerctl not found"

    def _system_info(self) -> tuple[bool, str]:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        uptime = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        info   = f"Disk:\n{result.stdout}\nUptime: {uptime.stdout}"
        print(info)
        return True, "System info displayed"

    def _empty_trash(self) -> tuple[bool, str]:
        subprocess.run(["gio", "trash", "--empty"], capture_output=True)
        return True, "Trash emptied"

    def _dark_mode(self, dark: bool) -> tuple[bool, str]:
        theme = "prefer-dark" if dark else "prefer-light"
        subprocess.run([
            "gsettings", "set",
            "org.gnome.desktop.interface",
            "color-scheme", theme
        ], capture_output=True)
        return True, f"{'Dark' if dark else 'Light'} mode enabled"


# ── Rule Matcher ──────────────────────────────────────────────────────────────────
class RuleMatcher:
    def __init__(self, rules_path: str = "config/rules.yaml"):
        self.rules: list[dict] = []
        self._load(rules_path)

    def _load(self, path: str):
        try:
            with open(path) as f:
                raw = yaml.safe_load(f) or {}
            for rule in raw.get("rules", []):
                action  = rule.get("action")
                matches = rule.get("match", [])
                extra   = {k: v for k, v in rule.items() if k not in ("action", "match")}
                if not action:
                    continue
                patterns = []
                for phrase in matches:
                    escaped = re.escape(phrase.lower())
                    escaped = re.sub(r"\\\{(\w+)\\\}", r"(?P<\1>.+)", escaped)
                    patterns.append({
                        "raw":       phrase.lower(),
                        "has_param": "{" in phrase,
                        "regex":     re.compile(f"^{escaped}$", re.IGNORECASE),
                    })
                self.rules.append({
                    "action":   action,
                    "patterns": patterns,
                    "extra":    extra,
                })
        except FileNotFoundError:
            log.warning(f"rules.yaml not found at {path}")

    def match(self, text: str) -> dict | None:
        t = text.lower().strip()

        # exact match
        for rule in self.rules:
            for p in rule["patterns"]:
                if not p["has_param"] and t == p["raw"]:
                    return self._build(rule, {})

        # contains match
        for rule in self.rules:
            for p in rule["patterns"]:
                if not p["has_param"] and p["raw"] in t:
                    return self._build(rule, {})

        # parameterized
        for rule in self.rules:
            for p in rule["patterns"]:
                if p["has_param"]:
                    m = p["regex"].match(t)
                    if m:
                        return self._build(rule, m.groupdict())
        return None

    def _build(self, rule: dict, params: dict) -> dict:
        merged = {**rule["extra"], **params}
        result = {"type": "action", "action": rule["action"], "params": merged}
        result.update(rule["extra"])
        return result


# ── System Context ────────────────────────────────────────────────────────────────
def build_context(prefs: dict) -> str:
    snap_path = Path("config/system_snapshot.json")
    apps_line = "unknown"
    if snap_path.exists():
        try:
            snap = json.loads(snap_path.read_text())
            apps = snap.get("installed_apps") or snap.get("apps") or []
            if apps and isinstance(apps[0], dict):
                names = [a.get("name", "") for a in apps[:40]]
            else:
                names = apps[:40]
            apps_line = ", ".join(names)
        except Exception:
            pass

    return "\n".join([
        "=== SYSTEM ===",
        "OS: Linux (Ubuntu)",
        f"Home: {prefs.get('home_dir', Path.home())}",
        f"Music app: {prefs.get('music_app', 'spotify')}",
        f"Browser: {prefs.get('browser', 'firefox')}",
        f"Installed apps (sample): {apps_line}",
        "==============",
    ])


# ── Assistant ─────────────────────────────────────────────────────────────────────
class Assistant:
    def __init__(self, prefs: dict):
        self.prefs    = prefs
        resolver      = AppResolver(prefs.get("apps_dir", "/usr/share/applications"))
        context       = build_context(prefs)

        self.rules    = RuleMatcher("config/rules.yaml")
        self.llm      = LLM(prefs.get("model", "llama3"), context)
        self.executor = Executor(prefs, resolver)
        self.memory   = Memory()
        log.info("Assistant ready.")

    def process(self, user_input: str):
        user_input = user_input.strip()
        if not user_input:
            return

        log.info(f"Input: {user_input!r}")

        # repeat
        if user_input.lower() in ("repeat", "again", "do that again"):
            last = self.memory.last_action()
            if last:
                self._execute(last, user_input)
            else:
                print("No previous action.")
            return

        # rule match (fast, no LLM)
        action = self.rules.match(user_input)
        if action:
            log.info(f"Rule matched: {action.get('action')}")
            self._execute(action, user_input)
            return

        # LLM (only when rules don't match)
        log.info("No rule match — calling LLM...")
        action = self.llm.ask(user_input, self.memory.format_history())
        if not action:
            print("Assistant: I couldn't understand that. Could you rephrase?")
            return

        self._execute(action, user_input)

    def _execute(self, action: dict, user_input: str):
        if action.get("type") == "chat":
            msg = action.get("message", "")
            print(f"\nAssistant: {msg}\n")
            self.memory.add(user_input, msg)
            return

        if action.get("type") == "clarify":
            question = action.get("question", "Could you clarify?")
            print(f"\nAssistant: {question}")
            followup = input("You: ").strip()
            if followup:
                self.process(f"{user_input}. {followup}")
            return

        success, msg = self.executor.run(action)
        icon = "✓" if success else "✗"
        print(f"\n[{icon}] {msg}\n")

        if success:
            self.memory.save_action(action)
            self.memory.add(user_input, msg)


# ── Main ──────────────────────────────────────────────────────────────────────────
def main():
    print("Starting assistant...")
    prefs     = load_prefs()
    assistant = Assistant(prefs)
    print("\nAssistant ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye.")
            break

        assistant.process(user_input)


if __name__ == "__main__":
    main()
