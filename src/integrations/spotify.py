import webbrowser
from urllib.parse import quote
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpotifyIntegration:
    """
    Open-App Mode Spotify (Jarvis-style safe fallback)
    No API dependency, no auth issues, always works.
    """

    def __init__(self):
        logger.info("Spotify running in OPEN-APP MODE")

    # =========================================================
    # SEARCH (OPENS SPOTIFY SEARCH PAGE)
    # =========================================================
    def search_track(self, query: str):
        try:
            url = f"https://open.spotify.com/search/{quote(query)}"
            webbrowser.open(url)

            return {
                "mode": "open_app",
                "query": query,
                "url": url,
                "message": "Opened Spotify search"
            }

        except Exception as e:
            logger.error(f"Spotify open error: {e}")
            return None

    # =========================================================
    # PLAY TRACK (ALSO OPENS SEARCH)
    # =========================================================
    def play(self, query: str):
        try:
            url = f"https://open.spotify.com/search/{quote(query)}"
            webbrowser.open(url)

            return {
                "mode": "open_app",
                "action": "play_request",
                "query": query,
                "url": url,
                "message": "Opened Spotify for playback"
            }

        except Exception as e:
            logger.error(f"Play error: {e}")
            return None

    # =========================================================
    # CONTROL COMMANDS (OPEN APP ONLY)
    # =========================================================
    def pause(self):
        return {
            "mode": "manual",
            "message": "Pause manually in Spotify app"
        }

    def next(self):
        return {
            "mode": "manual",
            "message": "Skip track manually in Spotify app"
        }

    def previous(self):
        return {
            "mode": "manual",
            "message": "Go to previous track manually in Spotify app"
        }
