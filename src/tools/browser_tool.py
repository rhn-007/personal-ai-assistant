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

        # Stores the most recent search results
        self.last_search_results = []

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

        # ---------------------------------------------
        # REMOVE COMMAND PHRASES
        # ---------------------------------------------

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

        # ---------------------------------------------
        # REMOVE SEARCH COMMAND PHRASES
        # ---------------------------------------------

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

        # ---------------------------------------------
        # CREATE GOOGLE SEARCH URL
        # ---------------------------------------------

        search_url = (

            "https://www.google.com/search?q="

            + quote(search_query)

        )

        # ---------------------------------------------
        # OPEN SEARCH IN BROWSER
        # ---------------------------------------------

        webbrowser.open(
            search_url
        )

        # ---------------------------------------------
        # FETCH SEARCH RESULTS
        # ---------------------------------------------

        try:

            response = requests.get(

                search_url,

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

            results = []

            # -----------------------------------------
            # FIND GOOGLE SEARCH RESULT HEADINGS
            # -----------------------------------------

            for heading in soup.find_all(
                "h3"
            ):

                title = heading.get_text(
                    " ",
                    strip=True
                )

                link = heading.find_parent(
                    "a"
                )

                if not link:

                    continue

                url = link.get(
                    "href"
                )

                if not url:

                    continue

                # -------------------------------------
                # CLEAN GOOGLE REDIRECT URL
                # -------------------------------------

                if url.startswith(
                    "/url?q="
                ):

                    url = url.split(
                        "/url?q=",
                        1
                    )[1]

                    url = url.split(
                        "&",
                        1
                    )[0]

                elif url.startswith(
                    "/url?"
                ):

                    continue

                # -------------------------------------
                # ONLY KEEP REAL HTTP URLS
                # -------------------------------------

                if not (

                    url.startswith(
                        "http://"
                    )

                    or url.startswith(
                        "https://"
                    )

                ):

                    continue

                # -------------------------------------
                # AVOID DUPLICATES
                # -------------------------------------

                if any(

                    result["url"] == url

                    for result in results

                ):

                    continue

                results.append(

                    {

                        "title": title,

                        "url": url

                    }

                )

                # Keep maximum 10 results

                if len(results) >= 10:

                    break

            # -----------------------------------------
            # SAVE RESULTS FOR LATER
            # -----------------------------------------

            self.last_search_results = results

            logger.info(

                f"Performed web search: "
                f"{search_query}"

            )

            # -----------------------------------------
            # FORMAT RESULTS
            # -----------------------------------------

            if results:

                output = [

                    f"🔎 Search results for: "
                    f"{search_query}\n"

                ]

                for index, result in enumerate(

                    results,

                    start=1

                ):

                    output.append(

                        f"{index}. "
                        f"{result['title']}\n"
                        f"   {result['url']}"

                    )

                output.append(

                    "\nYou can say "
                    "'open result 1' or "
                    "'read result 2'."

                )

                return "\n".join(
                    output
                )

            # -----------------------------------------
            # FALLBACK
            # -----------------------------------------

            return (

                f"🔎 Searching the web for "
                f"'{search_query}'.\n\n"

                "No readable search results "
                "were found."

            )

        except requests.RequestException as e:

            logger.error(

                f"Search request failed: "
                f"{e}"

            )

            return (

                f"🔎 Searching the web for "
                f"'{search_query}'."

            )

        except Exception as e:

            logger.error(

                f"Search parsing error: "
                f"{e}"

            )

            return (

                f"🔎 Searching the web for "
                f"'{search_query}'."

            )

    # =====================================================
    # OPEN SEARCH RESULT
    # =====================================================

    def open_result(self, number):

        if not self.last_search_results:

            return (

                "There are no recent search "
                "results."

            )

        try:

            index = int(number) - 1

        except ValueError:

            return (

                "Please specify a valid result "
                "number."

            )

        if (

            index < 0

            or index >= len(
                self.last_search_results
            )

        ):

            return (

                "That search result does "
                "not exist."

            )

        result = (

            self.last_search_results[
                index
            ]

        )

        webbrowser.open(
            result["url"]
        )

        logger.info(

            f"Opened search result "
            f"{number}: {result['url']}"

        )

        return (

            f"🌐 Opened result {number}: "
            f"{result['title']}"

        )

    # =====================================================
    # READ SEARCH RESULT
    # =====================================================

    def read_result(self, number):

        if not self.last_search_results:

            return (

                "There are no recent search "
                "results."

            )

        try:

            index = int(number) - 1

        except ValueError:

            return (

                "Please specify a valid result "
                "number."

            )

        if (

            index < 0

            or index >= len(
                self.last_search_results
            )

        ):

            return (

                "That search result does "
                "not exist."

            )

        result = (

            self.last_search_results[
                index
            ]

        )

        logger.info(

            f"Reading search result "
            f"{number}: {result['url']}"

        )

        return self.read_webpage(
            result["url"]
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

            # Remove trailing punctuation

            url = url.rstrip(
                ".,!?;)"
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

                    "form",

                    "noscript",

                    " 광고"

                ]

            ):

                element.decompose()

            # ---------------------------------------------
            # EXTRACT TEXT WITH STRUCTURE
            # ---------------------------------------------

            paragraphs = []

            for element in soup.find_all(

                [

                    "h1",

                    "h2",

                    "h3",

                    "h4",

                    "p",

                    "li"

                ]

            ):

                content = element.get_text(

                    " ",

                    strip=True

                )

                if content:

                    paragraphs.append(
                        content
                    )

            # ---------------------------------------------
            # FALLBACK
            # ---------------------------------------------

            if not paragraphs:

                text = soup.get_text(

                    separator=" ",

                    strip=True

                )

                paragraphs = [

                    text

                ]

            # ---------------------------------------------
            # REMOVE DUPLICATE CONSECUTIVE TEXT
            # ---------------------------------------------

            cleaned_paragraphs = []

            previous = None

            for paragraph in paragraphs:

                if paragraph == previous:

                    continue

                cleaned_paragraphs.append(
                    paragraph
                )

                previous = paragraph

            # ---------------------------------------------
            # JOIN WITH PARAGRAPH SPACING
            # ---------------------------------------------

            text = "\n\n".join(

                cleaned_paragraphs

            )

            if not text.strip():

                return (

                    "Could not extract text "
                    "from this webpage."

                )

            # ---------------------------------------------
            # LIMIT OUTPUT SIZE
            # ---------------------------------------------

            text = text[:10000]

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

        # ---------------------------------------------
        # OPEN WEBSITE
        # ---------------------------------------------

        if action == "open":

            return self.open_website(
                query
            )

        # ---------------------------------------------
        # SEARCH WEB
        # ---------------------------------------------

        if action == "search":

            return self.search_web(
                query
            )

        # ---------------------------------------------
        # READ WEBPAGE
        # ---------------------------------------------

        if action == "read":

            return self.read_webpage(
                query
            )

        # ---------------------------------------------
        # OPEN SEARCH RESULT
        # ---------------------------------------------

        if action == "open_result":

            return self.open_result(
                query
            )

        # ---------------------------------------------
        # READ SEARCH RESULT
        # ---------------------------------------------

        if action == "read_result":

            return self.read_result(
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
