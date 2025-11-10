import sys
from urllib.request import urlopen
from html.parser import HTMLParser
import requests
from bs4 import BeautifulSoup


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and self.title is None:
            self.title = data.strip()


class TextParser(HTMLParser):
    def __init__(self, max_chars=None):
        super().__init__()
        self.text_parts = []
        self.ignore_tags = {'script', 'style', 'noscript'}
        self.in_ignored_tag = False
        self.max_chars = max_chars
        self.total_chars = 0
        self.limit_reached = False

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            self.in_ignored_tag = True

    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            self.in_ignored_tag = False

    def handle_data(self, data):
        if not self.in_ignored_tag and not self.limit_reached:
            text = data.strip()
            if text:
                if self.max_chars is not None:
                    remaining = self.max_chars - self.total_chars
                    if remaining <= 0:
                        self.limit_reached = True
                        return
                    if len(text) > remaining:
                        text = text[:remaining]
                        self.limit_reached = True
                self.text_parts.append(text)
                self.total_chars += len(text)


def get_title_from_url(url):
    """Fetch the webpage and extract the title."""
    with urlopen(url, timeout=10) as response:
        html = response.read().decode('utf-8', errors='ignore')

    parser = TitleParser()
    parser.feed(html)

    if parser.title:
        return parser.title
    else:
        print("Error: Could not extract title from URL", file=sys.stderr)
        sys.exit(1)


def get_text_from_url(url, max_chars=None):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract full text
        text = soup.get_text(separator=" ", strip=True)

        return text[:max_chars]
    
    except Exception as e:
        print(f"Warning: Could not get text from URL: {url}")
        print(e)
        return None
