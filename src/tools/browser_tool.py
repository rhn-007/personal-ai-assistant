import re
import webbrowser
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class BrowserTool:

    def __init__(self, llm=None):

        self.name = "browser"

        # =================================================
        # OLLAMA LLM INTEGRATION
        # =================================================

        self.llm = llm

        # =================================================
        # SEARCH MEMORY
        # =================================================

        self.last_search_results = []

        # =================================================
        # WEBPAGE MEMORY
        # =================================================

        self.last_page_url = None
        self.last_page_text = None
        self.last_summary = None

        # =================================================
        # HTTP SETTINGS
        # =================================================

        self.timeout = 10

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        logger.info(
            "BrowserTool initialized"
        )

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        if not query or not isinstance(query, str):

            return False

        text = query.lower().strip()

        browser_phrases = [

            # ---------------------------------------------
            # WEBSITE OPENING
            # ---------------------------------------------

            "open youtube",
            "open google",
            "open github",
            "open wikipedia",
            "open chatgpt",
            "open reddit",
            "open instagram",
            "open facebook",
            "open twitter",
            "open x",
            "open website",
            "open browser",

            "go to",
            "visit",
            "browse",

            # ---------------------------------------------
            # SEARCH
            # ---------------------------------------------

            "search",
            "search for",
            "look up",
            "find online",
            "google",

            # ---------------------------------------------
            # READING
            # ---------------------------------------------

            "read ",
            "read this webpage",
            "read this website",
            "extract text from",

            # ---------------------------------------------
            # SUMMARIZATION
            # ---------------------------------------------

            "summarize ",
            "summarise ",

            # ---------------------------------------------
            # SUMMARY FOLLOW-UPS
            # ---------------------------------------------

            "longer summary",
            "longer summarize",
            "give a longer summary",
            "expand the summary",
            "expand that summary",
            "make the summary longer",
            "make it longer",
            "more detailed summary",
            "expand it",
            "elaborate on the summary",

            # ---------------------------------------------
            # SEARCH RESULT ACTIONS
            # ---------------------------------------------

            "open result",
            "read result",
            "open search result",
            "read search result"

        ]

        return (

            text.startswith("http://")

            or text.startswith("https://")

            or any(
                phrase in text
                for phrase in browser_phrases
            )

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
        # REMOVE COMMAND PREFIXES
        # ---------------------------------------------

        prefixes = [

            "open",
            "go to",
            "visit",
            "browse"

        ]

        for phrase in prefixes:

            if target.startswith(phrase):

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

            target.startswith("http://")

            or target.startswith("https://")

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

        search_query = query.lower().strip()

        phrases_to_remove = [

            "search for",
            "search",
            "look up",
            "find online",
            "google"

        ]

        for phrase in phrases_to_remove:

            if search_query.startswith(phrase):

                search_query = search_query[
                    len(phrase):
                ].strip()

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

        try:

            response = requests.get(

                search_url,

                timeout=self.timeout,

                headers=self.headers

            )

            response.raise_for_status()

            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )

            results = []

            for heading in soup.find_all("h3"):

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

                # -----------------------------------------
                # CLEAN GOOGLE REDIRECT URL
                # -----------------------------------------

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

                # -----------------------------------------
                # ONLY KEEP HTTP URLS
                # -----------------------------------------

                if not (

                    url.startswith(
                        "http://"
                    )

                    or url.startswith(
                        "https://"
                    )

                ):

                    continue

                # -----------------------------------------
                # AVOID DUPLICATES
                # -----------------------------------------

                if any(

                    result["url"] == url

                    for result in results

                ):

                    continue

                results.append({

                    "title":
                        title,

                    "url":
                        url

                })

                if len(results) >= 10:

                    break

            self.last_search_results = results

            logger.info(

                f"Performed web search: "
                f"{search_query}"

            )

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

        except (
            ValueError,
            TypeError
        ):

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

        except (
            ValueError,
            TypeError
        ):

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
    # EXTRACT URL
    # =====================================================

    def extract_url(self, query):

        if not query:

            return None

        query = query.strip()

        # ---------------------------------------------
        # EXTRACT URL FROM COMMAND
        # ---------------------------------------------

        url_match = re.search(

            r"https?://[^\s]+",

            query

        )

        if url_match:

            url = url_match.group(
                0
            )

            return url.rstrip(
                ".,!?;"
            )

        # ---------------------------------------------
        # REMOVE COMMAND PREFIXES
        # ---------------------------------------------

        prefixes = [

            "read this webpage",
            "read this website",
            "read webpage",
            "read website",

            "summarize this webpage",
            "summarize this website",
            "summarize webpage",
            "summarize website",
            "summarize",

            "summarise this webpage",
            "summarise this website",
            "summarise webpage",
            "summarise website",
            "summarise",

            "read"

        ]

        lower_query = query.lower()

        for prefix in prefixes:

            if lower_query.startswith(
                prefix
            ):

                query = query[
                    len(prefix):
                ].strip()

                break

        if not query:

            return None

        if not (

            query.startswith(
                "http://"
            )

            or query.startswith(
                "https://"
            )

        ):

            query = (
                "https://"
                + query
            )

        return query

    # =====================================================
    # EXTRACT WEBPAGE TEXT
    # =====================================================

    def extract_webpage_text(self, url):

        try:

            logger.info(
                f"Fetching webpage: {url}"
            )

            response = requests.get(

                url,

                timeout=self.timeout,

                headers=self.headers

            )

            response.raise_for_status()

            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )

            # ---------------------------------------------
            # REMOVE UNNECESSARY ELEMENTS
            # ---------------------------------------------

            for element in soup.find_all([

                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "noscript",
                "svg",
                "iframe"

            ]):

                element.decompose()

            # ---------------------------------------------
            # EXTRACT CONTENT
            # ---------------------------------------------

            paragraphs = []

            for element in soup.find_all([

                "h1",
                "h2",
                "h3",
                "h4",
                "p",
                "li"

            ]):

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

            text = "\n\n".join(
                cleaned_paragraphs
            )

            if not text.strip():

                return None

            # ---------------------------------------------
            # LIMIT CONTENT
            # ---------------------------------------------

            return text[:10000]

        except requests.RequestException as e:

            logger.error(

                f"Failed to access webpage "
                f"{url}: {e}"

            )

            return None

        except Exception as e:

            logger.error(

                f"Webpage extraction error: "
                f"{e}"

            )

            return None

    # =====================================================
    # READ WEBPAGE
    # =====================================================

    def read_webpage(self, query):

        if not query:

            return (
                "No webpage URL specified."
            )

        url = self.extract_url(
            query
        )

        if not url:

            return (

                "Please provide a valid "
                "webpage URL."

            )

        text = self.extract_webpage_text(
            url
        )

        if not text:

            return (

                "❌ Could not extract text "
                "from this webpage."

            )

        # ---------------------------------------------
        # SAVE LAST PAGE
        # ---------------------------------------------

        self.last_page_url = url
        self.last_page_text = text
        self.last_summary = None

        logger.info(

            f"Successfully read webpage: "
            f"{url}"

        )

        return (

            "📄 Webpage content:\n\n"
            + text

        )

    # =====================================================
    # FAST FALLBACK SUMMARY
    # =====================================================

    def basic_summary(self, text):

        if not text:

            return (
                "Could not generate a summary."
            )

        sentences = re.split(

            r"(?<=[.!?])\s+",

            text

        )

        sentences = [

            sentence.strip()

            for sentence in sentences

            if len(
                sentence.strip()
            ) > 40

        ]

        if not sentences:

            return text[:1500]

        return " ".join(

            sentences[:8]

        )

    # =====================================================
    # SUMMARIZE WEBPAGE
    # =====================================================

    def summarize_webpage(self, query):

        if not query:

            return (

                "No webpage URL specified."

            )

        # ---------------------------------------------
        # EXTRACT URL
        # ---------------------------------------------

        url = self.extract_url(
            query
        )

        if not url:

            return (

                "Please provide a valid "
                "webpage URL."

            )

        logger.info(

            f"Starting webpage summarization: "
            f"{url}"

        )

        # ---------------------------------------------
        # EXTRACT PAGE CONTENT
        # ---------------------------------------------

        webpage_text = (
            self.extract_webpage_text(
                url
            )
        )

        if not webpage_text:

            return (

                "❌ Could not extract text "
                "from this webpage."

            )

        # ---------------------------------------------
        # SAVE PAGE MEMORY
        # ---------------------------------------------

        self.last_page_url = url
        self.last_page_text = webpage_text
        self.last_summary = None

        # ---------------------------------------------
        # FALLBACK IF LLM UNAVAILABLE
        # ---------------------------------------------

        if not self.llm:

            logger.warning(

                "LLM unavailable. "
                "Using basic summary."

            )

            summary = (
                self.basic_summary(
                    webpage_text
                )
            )

            self.last_summary = summary

            return (

                "📝 Summary:\n\n"
                + summary

            )

        # ---------------------------------------------
        # LIMIT CONTENT SENT TO OLLAMA
        # ---------------------------------------------

        webpage_text = webpage_text[:8000]

        # ---------------------------------------------
        # SUMMARY PROMPT
        # ---------------------------------------------

        prompt = f"""
You are summarizing a webpage.

Use ONLY the webpage content provided below.

Important rules:

- Do not use user memory.
- Do not describe the user.
- Do not invent information.
- Do not use information from previous unrelated conversations.
- Identify the main topic.
- Mention the most important facts.
- Keep the summary under 300 words.
- Use bullet points when useful.

WEBPAGE URL:
{url}

WEBPAGE CONTENT:
{webpage_text}
"""

        try:

            logger.info(

                "Sending webpage content "
                "to Ollama..."

            )

            summary = (
                self.llm.generate_response(
                    prompt
                )
            )

            if not summary:

                logger.warning(

                    "Ollama returned an "
                    "empty response."

                )

                summary = (
                    self.basic_summary(
                        webpage_text
                    )
                )

            # -----------------------------------------
            # SAVE SUMMARY
            # -----------------------------------------

            self.last_summary = summary

            logger.info(

                "Successfully generated "
                "AI summary."

            )

            return (

                "📝 AI Summary:\n\n"
                + summary

            )

        except Exception as e:

            logger.error(

                f"AI summarization failed: "
                f"{e}"

            )

            summary = (
                self.basic_summary(
                    webpage_text
                )
            )

            self.last_summary = summary

            return (

                "📝 Summary:\n\n"
                + summary

            )

    # =====================================================
    # SUMMARIZE LAST PAGE
    # =====================================================

    def summarize_last_page(self, query=None):

        if not self.last_page_text:

            return (

                "❌ There is no recently "
                "summarized webpage to expand."

            )

        # ---------------------------------------------
        # DEFAULT WORD COUNT
        # ---------------------------------------------

        word_count = 300

        # ---------------------------------------------
        # EXTRACT REQUESTED WORD COUNT
        # ---------------------------------------------

        if query:

            match = re.search(

                r"(\d+)\s*words?",

                query.lower()

            )

            if match:

                word_count = int(
                    match.group(1)
                )

        # ---------------------------------------------
        # LLM FALLBACK
        # ---------------------------------------------

        if not self.llm:

            return (

                "❌ AI summarization is "
                "currently unavailable."

            )

        # ---------------------------------------------
        # USE ORIGINAL PAGE CONTENT
        # ---------------------------------------------

        webpage_text = (
            self.last_page_text[:10000]
        )

        prompt = f"""
You previously summarized a webpage.

Create a longer and more detailed summary
of the SAME webpage.

Requirements:

- Write approximately {word_count} words.
- Use ONLY information from the webpage content.
- Do not use personal memory.
- Do not describe the user.
- Do not talk about Rohan.
- Do not invent information.
- Preserve the important facts from the article.
- Explain the main topic clearly.
- Include relevant details and context.
- Use paragraphs or bullet points where useful.

WEBPAGE URL:
{self.last_page_url}

ORIGINAL WEBPAGE CONTENT:
{webpage_text}
"""

        try:

            logger.info(

                "Generating expanded summary "
                "of last webpage..."

            )

            summary = (
                self.llm.generate_response(
                    prompt
                )
            )

            if not summary:

                return (

                    "❌ Could not generate "
                    "an expanded summary."

                )

            self.last_summary = summary

            return (

                f"📝 Expanded Summary "
                f"(approximately {word_count} words):\n\n"

                + summary

            )

        except Exception as e:

            logger.error(

                f"Expanded summary failed: "
                f"{e}"

            )

            return (

                f"❌ Error generating "
                f"expanded summary: {e}"

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
        # OPEN
        # ---------------------------------------------

        if action == "open":

            return self.open_website(
                query
            )

        # ---------------------------------------------
        # SEARCH
        # ---------------------------------------------

        if action == "search":

            return self.search_web(
                query
            )

        # ---------------------------------------------
        # READ
        # ---------------------------------------------

        if action == "read":

            return self.read_webpage(
                query
            )

        # ---------------------------------------------
        # SUMMARIZE
        # ---------------------------------------------

        if action == "summarize":

            return self.summarize_webpage(
                query
            )

        # ---------------------------------------------
        # SUMMARIZE LAST PAGE
        # ---------------------------------------------

        if action == "summarize_last":

            return self.summarize_last_page(
                query
            )

        # ---------------------------------------------
        # OPEN RESULT
        # ---------------------------------------------

        if action == "open_result":

            return self.open_result(
                query
            )

        # ---------------------------------------------
        # READ RESULT
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
