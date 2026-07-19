from src.integrations.spotify import SpotifyIntegration
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SpotifyTool:

    def __init__(self):

        self.name = "spotify"

        self.spotify = SpotifyIntegration()

        logger.info(
            "SpotifyTool initialized successfully"
        )

    def execute_action(
        self,
        action: str,
        query: str
    ):

        if action == "play":

            return self.spotify.play(
                query
            )

        if action == "pause":

            return self.spotify.pause()

        if action == "next":

            return self.spotify.next()

        if action == "previous":

            return self.spotify.previous()

        return (
            f"Spotify command not recognized: "
            f"{action}"
        )

    def execute(self, query: str):

        return self.execute_action(
            "play",
            query
        )
