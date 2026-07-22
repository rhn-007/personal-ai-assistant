import webbrowser
from urllib.parse import quote

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class BrowserTool:

    def __init__(self):

        self.name = "browser"

        logger.info(
            "BrowserTool initialized"
        )

    # =====================================================
    # OPEN WEBSITE
    # =====================================================

    def open_website(self, query):

        if not query:

            return (
                "No website specified."
            )

        text = query.lower().strip()

        websites = {

            "youtube":
                "https://www.youtube.com",

            "google":
                "https://www.google.com",

            "github":
                "https://github.com",

            "wikipedia":
                "https://www.wikipedia.org",

            "chatgpt":
                "https://chatgpt.com",

            "reddit":
                "https://www.reddit.com",

            "instagram":
                "https://www.instagram.com",

            "facebook":
                "https://www.facebook.com",

            "twitter":
                "https://twitter.com",

            "x":
                "https://x.com"

        }

        target = text

        for phrase in [

            "open",

            "go to",

            "visit",

            "browse"

        ]:

            target = target.replace(
                phrase,
                ""
            ).strip()

        if target in websites:

            url = websites[target]

            webbrowser.open(url)

            logger.info(
                f"Opened website: {target}"
            )

            return (
                f"🌐 Opened {target.title()}."
            )

        if (

            target.startswith(
                "http://"
            )

            or target.startswith(
                "https://"
            )

        ):

            webbrowser.open(target)

            return (
                f"🌐 Opened {target}."
            )

        return self.search_web(
            target
        )

    # =====================================================
    # SEARCH WEB
    # =====================================================

    def search_web(self, query):

        if not query:

            return (
                "No search query specified."
            )

        search_url = (

            "https://www.google.com/search?q="

            + quote(query)

        )

        webbrowser.open(
            search_url
        )

        logger.info(

            f"Performed web search: "
            f"{query}"

        )

        return (

            f"🔎 Searching the web for "
            f"'{query}'."

        )

    # =====================================================
    # EXECUTE ACTION
    # =====================================================

    def execute_action(

        self,

        action,

        query=None

    ):

        if action == "open":

            return self.open_website(
                query
            )

        if action == "search":

            return self.search_web(
                query
            )

        return (

            f"Unknown browser action: "
            f"{action}"

        )

    # =====================================================
    # TOOL MANAGER COMPATIBILITY
    # =====================================================

    def execute(self, query):

        return self.open_website(
            query
        )
