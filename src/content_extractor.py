"""
Extracts main article text and OG image from a given URL.

Two strategies for text:
1. BeautifulSoup primary -- lightweight, handles most sites
2. Falls back to fetching just the first chunk of readable text

Also extracts the Open Graph image (og:image) for LinkedIn posts.

Returns a dict with 'text' and 'image_url' keys, or None on failure.
"""

from typing import Optional
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class ContentExtractor:
    def __init__(self, max_chars: int = 8000, timeout: int = 15):
        self.max_chars = max_chars
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })

    def extract(self, url: str) -> Optional[str]:
        """Extract article text from URL. Returns truncated text or None."""
        result = self.extract_with_image(url)
        if result:
            return result["text"]
        return None

    def extract_with_image(self, url: str) -> Optional[dict]:
        """
        Extract article text and OG image from URL.
        Returns {'text': str, 'image_url': str|None} or None on failure.
        """
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None

            soup = BeautifulSoup(resp.text, "lxml")

            # Extract OG image
            image_url = self._extract_og_image(soup, url)

            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                tag.decompose()

            # Try common article containers in priority order
            article = (
                soup.find("article")
                or soup.find(class_=lambda c: c and any(
                    kw in c.lower() for kw in ["article", "post-content", "entry-content", "article-body"]
                ) if c else False)
                or soup.find("main")
                or soup.find("body")
            )

            if not article:
                return None

            paragraphs = article.find_all("p")
            text = "\n\n".join(
                p.get_text(strip=True)
                for p in paragraphs
                if len(p.get_text(strip=True)) > 40
            )

            if text and len(text) > 200:
                return {
                    "text": text[: self.max_chars],
                    "image_url": image_url,
                }

        except (requests.RequestException, Exception):
            return None
        return None

    def _extract_og_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract the Open Graph image URL from meta tags."""
        # Try og:image first
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            img_url = og_image["content"]
            # Handle relative URLs
            if img_url.startswith("/"):
                img_url = urljoin(base_url, img_url)
            return img_url

        # Try twitter:image as fallback
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            img_url = twitter_image["content"]
            if img_url.startswith("/"):
                img_url = urljoin(base_url, img_url)
            return img_url

        # Try twitter:image:src
        twitter_image_src = soup.find("meta", attrs={"name": "twitter:image:src"})
        if twitter_image_src and twitter_image_src.get("content"):
            img_url = twitter_image_src["content"]
            if img_url.startswith("/"):
                img_url = urljoin(base_url, img_url)
            return img_url

        return None

    def download_image(self, image_url: str) -> Optional[bytes]:
        """Download an image and return its bytes."""
        try:
            resp = self.session.get(image_url, timeout=self.timeout)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "image" in content_type:
                return resp.content
        except (requests.RequestException, Exception):
            pass
        return None
