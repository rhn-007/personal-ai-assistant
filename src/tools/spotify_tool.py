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
             if "play" in q:
                song = query.lower().replace("play", "").strip()
        
                if not song:
                    return "Please specify a song"
        
                self.spotify.play_song(song)
                return f"🎵 Playing {song} on Spotify"
        
            if "pause" in q:
                self.spotify.pause()
                return "⏸️ Paused Spotify"
        
            if "next" in q:
                self.spotify.next()
                return "⏭️ Next song"
        
            if "previous" in q:
                self.spotify.previous()
                return "⏮️ Previous song"
                
            return None

        except Exception as e:
            logger.error(f"Spotify tool error: {e}")
            return f"Spotify Error: {e}"
