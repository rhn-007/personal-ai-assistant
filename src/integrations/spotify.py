import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class SpotifyIntegration:
    """
    Clean Spotify API wrapper (fixed + minimal + working)
    """

    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope="user-modify-playback-state user-read-playback-state"
            )
        )

        logger.info("Spotify authentication successful")

    # -----------------------------
    # SEARCH TRACKS (FIXED METHOD)
    # -----------------------------
    def search_track(self, query: str):
        """
        Returns simplified track list
        """
        results = self.sp.search(q=query, limit=1, type="track")

        items = results.get("tracks", {}).get("items", [])

        if not items:
            return None

        track = items[0]

        return [{
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "uri": track["uri"]
        }]

    # -----------------------------
    # PLAY TRACK
    # -----------------------------
    def play(self, uri: str = None):
        if uri:
            self.sp.start_playback(uris=[uri])
        else:
            self.sp.start_playback()

    # -----------------------------
    # PAUSE
    # -----------------------------
    def pause(self):
        self.sp.pause_playback()

    # -----------------------------
    # NEXT
    # -----------------------------
    def next(self):
        self.sp.next_track()

    # -----------------------------
    # PREVIOUS
    # -----------------------------
    def previous(self):
        self.sp.previous_track()
