import os
import urllib.parse

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class SpotifyIntegration:

    def __init__(self):

        logger.info(
            "Spotify running in OPEN-APP SEARCH MODE"
        )

    def search_and_open(self, query: str):

        if not query:

            return "No song specified."

        # Remove common command words
        song = query.lower()

        for word in [
            "play",
            "open",
            "search",
            "find",
            "on spotify",
            "spotify"
        ]:

            song = song.replace(
                word,
                ""
            )

        song = song.strip()

        if not song:

            return "Please specify a song."

        # Encode the song name
        encoded_song = urllib.parse.quote(
            song
        )

        spotify_uri = (
            f"spotify:search:{encoded_song}"
        )

        try:

            os.startfile(
                spotify_uri
            )

            logger.info(
                f"Opened Spotify search for: {song}"
            )

            return (
                f"Opened Spotify search for "
                f"'{song}'."
            )

        except Exception as e:

            logger.error(
                f"Spotify app search failed: {e}"
            )

            return (
                f"Could not open Spotify search: "
                f"{e}"
            )

    def play(self, query: str):

        return self.search_and_open(
            query
        )

    def pause(self):

        return (
            "Pause control requires Spotify "
            "Premium API playback access."
        )

    def next(self):

        return (
            "Next-track control requires Spotify "
            "Premium API playback access."
        )

    def previous(self):

        return (
            "Previous-track control requires Spotify "
            "Premium API playback access."
        )
