from src.integrations.spotify import SpotifyIntegration
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpotifyTool:
    """
    Clean Spotify Tool (FIXED + consistent indentation)
    """

    def __init__(self):
        self.name = "spotify"
        self.spotify = SpotifyIntegration()

        logger.info("SpotifyTool initialized successfully")

    def can_handle(self, query: str) -> bool:
        if not query:
            return False

        q = query.lower()

        return any(k in q for k in [
            "spotify",
            "play",
            "pause",
            "next",
            "previous",
            "song",
            "music"
        ])

    def execute(self, query: str):
        q = query.lower()

        try:
            # PLAY SONG
            if "play" in q:
                song = q.replace("play", "").strip()

                if not song:
                    return "Please specify a song name"

                self.spotify.play_song(song)
                return f"🎵 Playing {song}"

            # PAUSE
            if "pause" in q:
                self.spotify.pause()
                return "⏸️ Paused Spotify"

            # NEXT
            if "next" in q:
                self.spotify.next()
                return "⏭️ Next song"

            # PREVIOUS
            if "previous" in q:
                self.spotify.previous()
                return "⏮️ Previous song"

            return "Spotify command not recognized"

        except Exception as e:
            logger.error(f"Spotify tool error: {e}")
            return f"Spotify Error: {e}"
