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
            if "play" in q:
                song = q.replace("play", "").strip()
    
                if not song:
                    return "Please specify a song name"
    
                result = self.spotify.search_track(song)
    
                if not result:
                    return "No song found"
    
                track = result[0]
    
                return f"🎵 Found: {track['name']} by {track['artist']}"
    
            return "Spotify ready"
    
        except Exception as e:
            return f"Spotify Error: {e}"
