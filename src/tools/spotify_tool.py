from src.utils.logger import setup_logger
from src.integrations.spotify import SpotifyIntegration

logger = setup_logger(__name__)


class SpotifyTool:
    """
    Tool wrapper for SpotifyIntegration
    Converts natural language actions → Spotify API calls
    """

    def __init__(self):
        self.name = "spotify"
        self.spotify = SpotifyIntegration()

    # ---------------- ROUTING ----------------

    def can_handle(self, query: str) -> bool:
        q = query.lower()
        return any(k in q for k in [
            "spotify", "play", "song", "music", "pause", "next", "previous", "volume"
        ])

    # ---------------- MAIN EXECUTION ----------------

    def execute(self, query: str):

        q = query.lower()

        try:
            # PLAY SONG
            if "play" in q:
                # remove trigger words
                clean_query = query.replace("play", "").strip()

                if not clean_query:
                    return "Please specify what to play"

                return self.spotify.play_song(clean_query)

            # PAUSE
            if "pause" in q:
                self.spotify.pause()
                return "Music paused"

            # NEXT
            if "next" in q:
                self.spotify.next()
                return "Next track"

            # PREVIOUS
            if "previous" in q:
                self.spotify.previous()
                return "Previous track"

            # VOLUME UP/DOWN (simple version)
            if "volume" in q:
                if "up" in q:
                    self.spotify.volume(80)
                    return "Volume increased"
                elif "down" in q:
                    self.spotify.volume(30)
                    return "Volume decreased"

            return "Spotify command not understood"

        except Exception as e:
            logger.error(f"Spotify tool error: {e}")
            return f"Spotify Error: {e}"
