import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpotifyIntegration:
    """
    Handles direct communication with Spotify API
    (NO tool logic here — only raw API actions)
    """

    def __init__(self):
        self.sp = None
        self.authenticate()

    # ---------------- AUTH ----------------

    def authenticate(self):
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope=" ".join([
                    "user-read-playback-state",
                    "user-modify-playback-state",
                    "user-read-currently-playing",
                    "user-library-read",
                    "playlist-read-private",
                    "playlist-read-collaborative"
                ])
            ))

            logger.info("Spotify authentication successful")

        except Exception as e:
            logger.error(f"Spotify auth failed: {e}")
            self.sp = None

    # ---------------- DEVICE ----------------

    def get_devices(self):
        if not self.sp:
            return None
        return self.sp.devices()

    def transfer_device(self, device_id):
        if not self.sp:
            return None
        return self.sp.transfer_playback(device_id)

    # ---------------- PLAYBACK CONTROL ----------------

    def play(self):
        return self.sp.start_playback()

    def pause(self):
        return self.sp.pause_playback()

    def next(self):
        return self.sp.next_track()

    def previous(self):
        return self.sp.previous_track()

    def volume(self, value: int):
        return self.sp.volume(value)

    def shuffle(self, state: bool):
        return self.sp.shuffle(state)

    def repeat(self, state: str = "off"):
        return self.sp.repeat(state)

    # ---------------- SEARCH ----------------

    def search_song(self, query: str):
        results = self.sp.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        return items[0] if items else None

    def search_playlist(self, query: str):
        results = self.sp.search(q=query, type="playlist", limit=1)
        items = results.get("playlists", {}).get("items", [])
        return items[0] if items else None

    def search_album(self, query: str):
        results = self.sp.search(q=query, type="album", limit=1)
        items = results.get("albums", {}).get("items", [])
        return items[0] if items else None

    # ---------------- PLAY ACTIONS ----------------

    def play_song(self, query: str):
        song = self.search_song(query)
        if not song:
            return "Song not found"

        uri = song["uri"]
        self.sp.start_playback(uris=[uri])
        return f"Playing: {song['name']}"

    def play_playlist(self, query: str):
        playlist = self.search_playlist(query)
        if not playlist:
            return "Playlist not found"

        uri = playlist["uri"]
        self.sp.start_playback(context_uri=uri)
        return f"Playing playlist: {playlist['name']}"

    def play_album(self, query: str):
        album = self.search_album(query)
        if not album:
            return "Album not found"

        uri = album["uri"]
        self.sp.start_playback(context_uri=uri)
        return f"Playing album: {album['name']}"

    # ---------------- STATUS ----------------

    def current_song(self):
        return self.sp.current_playback()
