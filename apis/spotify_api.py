import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyController:

    def __init__(self, prefs: dict):
        spotify_cfg = prefs.get("spotify", {})

        self.client_id = spotify_cfg.get("client_id")
        self.client_secret = spotify_cfg.get("client_secret")
        self.redirect_uri = spotify_cfg.get("redirect_uri")

        self.client = None

        self.scope = (
            "user-read-playback-state "
            "user-modify-playback-state "
            "user-read-currently-playing "
            "streaming"
        )

    # -----------------------------
    # AUTHENTICATE
    # -----------------------------
    def authenticate(self) -> bool:
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path="config/.spotify_token",
                open_browser=True
            )

            self.client = spotipy.Spotify(auth_manager=auth_manager)

            # test call
            self.client.current_user()

            return True

        except Exception as e:
            print(f"[Spotify Auth Failed] {e}")
            return False

    # -----------------------------
    # SEARCH + PLAY
    # -----------------------------
    def search_and_play(self, query: str) -> str:
        if not self.client:
            raise RuntimeError("Spotify not authenticated")

        results = self.client.search(q=query, type="track", limit=1)

        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            raise ValueError(f"Track not found: {query}")

        track = tracks[0]
        uri = track["uri"]

        device_id = self._get_active_device()

        self.client.start_playback(device_id=device_id, uris=[uri])

        name = track["name"]
        artist = track["artists"][0]["name"]

        return f"Now playing: {name} by {artist}"

    # -----------------------------
    # PAUSE
    # -----------------------------
    def pause(self) -> str:
        self.client.pause_playback()
        return "Paused"

    # -----------------------------
    # RESUME
    # -----------------------------
    def resume(self) -> str:
        self.client.start_playback()
        return "Resumed"

    # -----------------------------
    # SKIP
    # -----------------------------
    def skip(self) -> str:
        self.client.next_track()
        return "Skipped"

    # -----------------------------
    # VOLUME
    # -----------------------------
    def set_volume(self, level: int) -> str:
        if not (0 <= level <= 100):
            raise ValueError("Volume must be between 0 and 100")

        self.client.volume(level)
        return f"Volume set to {level}%"

    # -----------------------------
    # CURRENT TRACK
    # -----------------------------
    def get_current_track(self):
        data = self.client.current_playback()

        if not data or not data.get("item"):
            return None

        track = data["item"]

        return {
            "track": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "progress_ms": data["progress_ms"],
            "duration_ms": track["duration_ms"]
        }

    # -----------------------------
    # ACTIVE DEVICE
    # -----------------------------
    def _get_active_device(self):
        devices = self.client.devices().get("devices", [])

        for d in devices:
            if d.get("is_active"):
                return d["id"]

        raise RuntimeError("No active Spotify device found")
