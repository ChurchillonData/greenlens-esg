"""Generic web content fetcher: URL → clean plain text.

Uses requests + BeautifulSoup. Strips navigation, scripts, and boilerplate.
Returns the main article/body text, capped at max_chars.
"""

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_STRIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "iframe"}
_MIN_PARA_LEN = 40


def fetch_text(url: str, max_chars: int = 6000, timeout: int = 15) -> Optional[str]:
    """Fetch a URL and return extracted plain text, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    # Prefer semantic content containers; fall back to full body
    content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"class": re.compile(r"(content|post|entry|article)", re.I)})
        or soup.body
    )
    if content is None:
        return None

    parts = []
    for el in content.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
        text = el.get_text(separator=" ", strip=True)
        if len(text) >= _MIN_PARA_LEN:
            parts.append(text)

    body = "\n".join(parts)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body[:max_chars] or None
