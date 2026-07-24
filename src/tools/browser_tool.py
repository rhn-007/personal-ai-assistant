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

        # Ollama LLM integration
        self.llm = llm

        # Store the most recent search results
        self.last_search_results = []

        # Store the last webpage and summary
        self.last_page_url = None
        self.last_page_text = None
        self.last_summary = None

        # HTTP settings
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

        logger.info("BrowserTool initialized")

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        if not query or not isinstance(query, str):

            return False

        text = query.lower().strip()

        browser_phrases = [

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

            "search",
            "search for",
            "look up",
            "find online",
            "google",

            "read ",
            "read this webpage",
            "read this website",

            "summarize ",
            "summarise ",

            "open result",
            "read result",
            "open search result",
            "read search result",

            "extract text from"

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

            return "No website specified."

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

            return f"🌐 Opened {target}."

        # ---------------------------------------------
        # UNKNOWN TARGET → SEARCH
        # ---------------------------------------------

        return self.search_web(target)

    # =====================================================
    # SEARCH WEB
    # =====================================================

    def search_web(self, query):

        if not query:

            return "No search query specified."

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

        # ---------------------------------------------
        # OPEN GOOGLE SEARCH DIRECTLY
        # ---------------------------------------------

        search_url = (

            "https://www.google.com/search?q="
            + quote(search_query)

        )

        webbrowser.open(search_url)

        logger.info(
            f"Opened Google search for: "
            f"{search_query}"
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

        except (ValueError, TypeError):

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

        result = self.last_search_results[index]

        webbrowser.open(result["url"])

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

        except (ValueError, TypeError):

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

        result = self.last_search_results[index]

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

            url = url_match.group(0)

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

            if lower_query.startswith(prefix):

                query = query[
                    len(prefix):
                ].strip()

                break

        if not query:

            return None

        if not (

            query.startswith("http://")
            or query.startswith("https://")

        ):

            query = "https://" + query

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

                    paragraphs.append(content)

            # ---------------------------------------------
            # FALLBACK
            # ---------------------------------------------

            if not paragraphs:

                text = soup.get_text(

                    separator=" ",

                    strip=True

                )

                paragraphs = [text]

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
            # SAVE LAST PAGE
            # ---------------------------------------------

            self.last_page_url = url
            self.last_page_text = text[:10000]

            return self.last_page_text

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

            return "No webpage URL specified."

        url = self.extract_url(query)

        if not url:

            return (
                "Please provide a valid "
                "webpage URL."
            )

        text = self.extract_webpage_text(url)

        if not text:

            return (
                "❌ Could not extract text "
                "from this webpage."
            )

        logger.info(
            f"Successfully read webpage: {url}"
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

            if len(sentence.strip()) > 40

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

        url = self.extract_url(query)

        if not url:

            return (
                "Please provide a valid "
                "webpage URL."
            )

        logger.info(
            f"Starting webpage summarization: {url}"
        )

        # ---------------------------------------------
        # EXTRACT PAGE CONTENT
        # ---------------------------------------------

        webpage_text = self.extract_webpage_text(url)

        if not webpage_text:

            return (
                "❌ Could not extract text "
                "from this webpage."
            )

        # ---------------------------------------------
        # FALLBACK IF LLM IS UNAVAILABLE
        # ---------------------------------------------

        if not self.llm:

            logger.warning(
                "LLM unavailable. Using basic summary."
            )

            summary = self.basic_summary(
                webpage_text
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

        prompt = f"""
Summarize this webpage clearly and concisely.

Rules:

- Use only information from the webpage.
- Identify the main topic.
- Mention the most important facts.
- Do not invent information.
- Keep the answer under 300 words.
- Use bullet points when useful.
- Do not use information about the user.
- Do not talk about the user's personality, interests,
  background, or personal profile.
- Answer only about the webpage.

URL:
{url}

WEBPAGE CONTENT:
{webpage_text}
"""

        try:

            logger.info(
                "Sending webpage content to Ollama..."
            )

            summary = self.llm.generate_response(
                prompt
            )

            if not summary:

                logger.warning(
                    "Ollama returned an empty response."
                )

                summary = self.basic_summary(
                    webpage_text
                )

                self.last_summary = summary

                return (

                    "📝 Summary:\n\n"
                    + summary

                )

            self.last_summary = summary

            logger.info(
                "Successfully generated AI summary."
            )

            return (

                "📝 AI Summary:\n\n"
                + summary

            )

        except Exception as e:

            logger.error(

                f"AI summarization failed: {e}"

            )

            summary = self.basic_summary(
                webpage_text
            )

            self.last_summary = summary

            return (

                "📝 Summary:\n\n"
                + summary

            )

    # =====================================================
    # SUMMARIZE LAST PAGE
    # =====================================================

    def summarize_last(self, query=None):

        if not self.last_page_text:

            return (

                "❌ There is no webpage summary "
                "to update yet."

            )

        if not self.llm:

            summary = self.basic_summary(
                self.last_page_text
            )

            self.last_summary = summary

            return (

                "📝 Updated Summary:\n\n"
                + summary

            )

        prompt = f"""
Create an updated summary of the webpage below.

The user wants a longer or more detailed summary.

Rules:

- Use only the webpage content provided.
- Do not use any information about the user.
- Do not describe the user's personality,
  interests, background, or preferences.
- Do not invent facts.
- Preserve the important facts from the original webpage.
- Add useful details from the webpage.
- Aim for approximately 200 to 300 words unless
  the user specifically requests another word count.
- Return only the updated summary.
- Do not talk about these instructions.

Original webpage URL:
{self.last_page_url}

WEBPAGE CONTENT:
{self.last_page_text}
"""

        try:

            logger.info(
                "Generating updated webpage summary..."
            )

            summary = self.llm.generate_response(
                prompt
            )

            if not summary:

                summary = self.basic_summary(
                    self.last_page_text
                )

            self.last_summary = summary

            logger.info(
                "Successfully generated updated summary."
            )

            return (

                "📝 Updated Summary:\n\n"
                + summary

            )

        except Exception as e:

            logger.error(

                f"Updated summary generation failed: "
                f"{e}"

            )

            summary = self.basic_summary(
                self.last_page_text
            )

            self.last_summary = summary

            return (

                "📝 Updated Summary:\n\n"
                + summary

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

            return self.open_website(query)

        if action == "search":

            return self.search_web(query)

        if action == "read":

            return self.read_webpage(query)

        if action == "summarize":

            return self.summarize_webpage(query)

        if action == "summarize_last":

            return self.summarize_last(query)

        if action == "open_result":

            return self.open_result(query)

        if action == "read_result":

            return self.read_result(query)

        return (

            f"Unknown browser action: "
            f"{action}"

        )

    # =====================================================
    # TOOL MANAGER COMPATIBILITY
    # =====================================================

    def execute(self, query):

        return self.open_website(query)
