from src.integrations.spotify import SpotifyIntegration
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpotifyTool:
    """
    Clean Spotify Tool (Stable + No indentation issues)
    """

    def __init__(self):
        self.name = "spotify"
        self.spotify = SpotifyIntegration()

        logger.info("SpotifyTool initialized successfully")

    def can_handle(self, query: str) -> bool:
        if not query:
            return False

        q = query.lower()

        return any(
            k in q for k in [
                "spotify",
                "play",
                "pause",
                "next",
                "previous",
                "song",
                "music"
            ]
        )

    def execute(self, query: str):
        q = query.lower()

        try:
            # PLAY SONG
            if "play" in q:
                song = q.replace("play", "").strip()

                if not song:
                    return "Please specify a song name"

                result = self.spotify.search_track(song)

                if not result:
                    return "No song found"

                track = result[0]

                return f"🎵 Found: {track['name']} by {track['artist']}"

            # PAUSE
            if "pause" in q:
                self.spotify.pause()
                return "⏸️ Paused Spotify"

            # NEXT
            if "next" in q:
                self.spotify.next()
                return "⏭️ Next track"

            # PREVIOUS
            if "previous" in q:
                self.spotify.previous()
                return "⏮️ Previous track"

            return "Spotify command not recognized"

        except Exception as e:
            logger.error(f"Spotify tool error: {e}")
            return f"Spotify Error: {e}"
