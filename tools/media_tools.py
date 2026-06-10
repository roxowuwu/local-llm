import subprocess

# optional imports (safe fallback)
try:
    from apis.spotify_api import SpotifyController
except:
    SpotifyController = None

try:
    from tools import web_tools
except:
    web_tools = None


# -----------------------------
# MEDIA PLAY
# -----------------------------
def media_play(params: dict, prefs: dict):
    query = params.get("query")

    if not query:
        return "No query provided"

    music_app = prefs.get("music_app", "youtube")

    # 🎵 SPOTIFY
    if music_app == "spotify" and SpotifyController:
        try:
            SpotifyController().search_and_play(query)
            return f"Now playing: {query} on Spotify"
        except Exception:
            return "Spotify playback failed"

    # ▶️ YOUTUBE
    elif music_app == "youtube":
        url = f"https://www.youtube.com/results?search_query={query}"

        if web_tools:
            web_tools.open_url({"url": url}, prefs)
            return f"Opened YouTube search for: {query}"
        else:
            return "web_tools not available"

    # ⚙️ FALLBACK (playerctl)
    else:
        try:
            subprocess.run(["playerctl", "play"], check=True)
            return f"Playing: {query}"
        except:
            return "No media player available"


# -----------------------------
# PAUSE
# -----------------------------
def media_pause(params: dict, prefs: dict):
    try:
        subprocess.run(["playerctl", "pause"], check=True)
        return "Paused"
    except:
        return "Failed to pause"


# -----------------------------
# SKIP
# -----------------------------
def media_skip(params: dict, prefs: dict):
    try:
        subprocess.run(["playerctl", "next"], check=True)
        return "Skipped to next track"
    except:
        return "Failed to skip"


# -----------------------------
# VOLUME
# -----------------------------
def media_volume(params: dict, prefs: dict):
    level = params.get("level")

    if level is None:
        return "No volume level provided"

    try:
        level = int(level)
        level = max(0, min(100, level))  # clamp

        subprocess.run(
            ["playerctl", "volume", str(level / 100)],
            check=True
        )

        return f"Volume set to {level}%"
    except:
        return "Failed to set volume"
