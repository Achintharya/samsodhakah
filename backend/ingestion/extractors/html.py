"""
HTML content extraction — extracts readable text from web pages.
"""

from __future__ import annotations

import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HtmlExtractor:
    """Extract readable text content from HTML pages."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def extract(self, url: str, max_chars: int = 5000) -> Optional[str]:
        """
        Extract readable text from a URL.

        Args:
            url: The web page URL.
            max_chars: Maximum characters to extract (approximate).

        Returns:
            Extracted text content, or None on failure.
        """
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={"User-Agent": self.USER_AGENT},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            # Truncate if needed
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[...content truncated]"

            logger.info(f"Extracted {len(text)} chars from {url}")
            return text

        except requests.RequestException as e:
            logger.warning(f"Failed to extract from {url}: {e}")
            return None

    def extract_batch(
        self, urls: list[str], max_chars: int = 3000
    ) -> list[dict]:
        """
        Extract content from multiple URLs.

        Returns list of dicts with 'url', 'content', 'success' keys.
        """
        results = []
        for url in urls:
            content = self.extract(url, max_chars)
            results.append({
                "url": url,
                "content": content or "",
                "success": content is not None,
            })
        return results


# Global instance
html_extractor = HtmlExtractor()