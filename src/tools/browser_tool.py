import re
import webbrowser
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

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

            if target.startswith(
                phrase
            ):

                target = target[
                    len(phrase):
                ].strip()

                break

        # ---------------------------------------------
        # OPEN KNOWN WEBSITE
        # ---------------------------------------------

        if target in websites:

            url = websites[target]

            webbrowser.open(url)

            logger.info(
                f"Opened website: {target}"
            )

            return (
                f"🌐 Opened "
                f"{target.title()}."
            )

        # ---------------------------------------------
        # OPEN DIRECT URL
        # ---------------------------------------------

        if (

            target.startswith(
                "http://"
            )

            or target.startswith(
                "https://"
            )

        ):

            webbrowser.open(target)

            logger.info(
                f"Opened URL: {target}"
            )

            return (
                f"🌐 Opened {target}."
            )

        # ---------------------------------------------
        # UNKNOWN TARGET → SEARCH
        # ---------------------------------------------

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

        search_query = (
            query.lower().strip()
        )

        phrases_to_remove = [

            "search for",

            "search",

            "look up",

            "find online",

            "google"

        ]

        for phrase in phrases_to_remove:

            if search_query.startswith(
                phrase
            ):

                search_query = (

                    search_query[
                        len(phrase):
                    ]

                    .strip()

                )

                break

        if not search_query:

            return (

                "Please specify what you "
                "want me to search for."

            )

        search_url = (

            "https://www.google.com/search?q="

            + quote(search_query)

        )

        webbrowser.open(
            search_url
        )

        logger.info(

            f"Performed web search: "
            f"{search_query}"

        )

        return (

            f"🔎 Searching the web for "
            f"'{search_query}'."

        )

    # =====================================================
    # READ WEB PAGE
    # =====================================================

    def read_webpage(self, url):

        if not url:

            return (

                "No webpage URL specified."

            )

        url = url.strip()

        # ---------------------------------------------
        # EXTRACT URL FROM COMMAND
        # ---------------------------------------------

        url_match = re.search(

            r"https?://\S+",

            url

        )

        if url_match:

            url = url_match.group(
                0
            )

        else:

            prefixes = [

                "read this webpage",

                "read this website",

                "read webpage",

                "read website",

                "read"

            ]

            lower_url = (
                url.lower()
            )

            for prefix in prefixes:

                if lower_url.startswith(
                    prefix
                ):

                    url = url[
                        len(prefix):
                    ].strip()

                    break

            if not (

                url.startswith(
                    "http://"
                )

                or url.startswith(
                    "https://"
                )

            ):

                url = (

                    "https://"

                    + url

                )

        try:

            response = requests.get(

                url,

                timeout=10,

                headers={

                    "User-Agent":

                    "Mozilla/5.0"

                }

            )

            response.raise_for_status()

            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )

            # ---------------------------------------------
            # REMOVE NON-CONTENT ELEMENTS
            # ---------------------------------------------

            for element in soup(

                [

                    "script",

                    "style",

                    "nav",

                    "footer",

                    "header",

                    "aside",

                    "form"

                ]

            ):

                element.decompose()

            # ---------------------------------------------
            # EXTRACT TEXT
            # ---------------------------------------------

            text = soup.get_text(

                separator=" ",

                strip=True

            )

            if not text:

                return (

                    "Could not extract text "
                    "from this webpage."

                )

            # ---------------------------------------------
            # LIMIT OUTPUT SIZE
            # ---------------------------------------------

            text = text[:5000]

            logger.info(

                f"Successfully read webpage: "
                f"{url}"

            )

            return (

                f"📄 Webpage content:\n\n"

                f"{text}"

            )

        except requests.RequestException as e:

            logger.error(

                f"Failed to read webpage "
                f"{url}: {e}"

            )

            return (

                f"❌ Could not access webpage: "
                f"{e}"

            )

        except Exception as e:

            logger.error(

                f"Webpage reading error: "
                f"{e}"

            )

            return (

                f"❌ Error reading webpage: "
                f"{e}"

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

        if action == "read":

            return self.read_webpage(
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
