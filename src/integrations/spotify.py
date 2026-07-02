import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class SpotifyIntegration:
    """
    Clean Spotify API wrapper (stable + agent-ready + Jarvis-safe)
    """

    def __init__(self):
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                    scope="user-modify-playback-state user-read-playback-state"
                )
            )
            logger.info("Spotify authentication successful")

        except Exception as e:
            logger.error(f"Spotify init failed: {e}")
            self.sp = None

    # =========================================================
    # SEARCH TRACK (FIXED: returns SINGLE OBJECT)
    # =========================================================
    def search_track(self, query: str):
        try:
            if not self.sp:
                return None

            results = self.sp.search(q=query, limit=1, type="track")
            items = results.get("tracks", {}).get("items", [])

            if not items:
                return None

            track = items[0]

            return {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"],
                "url": track["external_urls"]["spotify"]
            }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return None

    # =========================================================
    # PLAY TRACK (SAFE)
    # =========================================================
    def play(self, uri: str = None):
        try:
            if not self.sp:
                return False

            if uri:
                self.sp.start_playback(uris=[uri])
            else:
                self.sp.start_playback()

            return True

        except Exception as e:
            logger.error(f"Play error: {e}")
            return False

    # =========================================================
    # PAUSE
    # =========================================================
    def pause(self):
        try:
            if not self.sp:
                return False

            self.sp.pause_playback()
            return True

        except Exception as e:
            logger.error(f"Pause error: {e}")
            return False

    # =========================================================
    # NEXT TRACK
    # =========================================================
    def next(self):
        try:
            if not self.sp:
                return False

            self.sp.next_track()
            return True

        except Exception as e:
            logger.error(f"Next error: {e}")
            return False

    # =========================================================
    # PREVIOUS TRACK
    # =========================================================
    def previous(self):
        try:
            if not self.sp:
                return False

            self.sp.previous_track()
            return True

        except Exception as e:
            logger.error(f"Previous error: {e}")
            return False
