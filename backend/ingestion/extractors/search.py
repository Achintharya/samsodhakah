"""
Web search module — DuckDuckGo primary, Serper API fallback.
Preserved and refactored from Akṣarajña backend web_context_extract.py.
"""

from __future__ import annotations

import random
import logging
from typing import Optional
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# DuckDuckGo search
try:
    from duckduckgo_search import DDGS
    HAS_DDG = True
except ImportError:
    HAS_DDG = False
    logger.warning("DuckDuckGo search not available. Install duckduckgo-search.")

# Async HTTP for Serper
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


async def search_duckduckgo(query: str, max_results: int = 5) -> list[str]:
    """Search using DuckDuckGo (free, no API key required)."""
    if not HAS_DDG:
        logger.warning("DuckDuckGo search unavailable (package not installed)")
        return []

    try:
        with DDGS() as search:
            results = search.text(query, max_results=max_results)
            urls = [r["href"] for r in results if "href" in r]
            logger.info(f"DuckDuckGo returned {len(urls)} results for: {query}")
            return urls[:max_results]
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []


async def search_serper(query: str, max_results: int = 6) -> list[str]:
    """Search using Serper API (premium fallback)."""
    api_key = settings.serper_api_key
    if not api_key:
        logger.warning("Serper API key not configured")
        return []

    if not HAS_AIOHTTP:
        logger.warning("aiohttp not available for Serper search")
        return []

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }
    payload = {"q": query, "gl": "in", "num": max_results}
    query_lower = query.lower()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                data = await response.json()

                results = []
                for result in data.get("organic", []):
                    link = result.get("link")
                    if not link or "youtube.com" in link or "youtu.be" in link:
                        continue

                    # Relevance scoring
                    score = 0
                    title = result.get("title", "").lower()
                    snippet = result.get("snippet", "").lower()
                    if query_lower in title:
                        score += 2
                    if query_lower in snippet:
                        score += 1

                    if score > 0:
                        results.append((score, link))

                results.sort(key=lambda x: x[0], reverse=True)
                urls = [link for score, link in results[:max_results]]
                logger.info(f"Serper returned {len(urls)} results for: {query}")
                return urls

    except Exception as e:
        logger.warning(f"Serper search failed: {e}")
        return []


async def search(query: str, max_results: int = 5) -> list[str]:
    """
    Search the web using DuckDuckGo with Serper fallback.
    Returns a list of relevant URLs.
    """
    urls = await search_duckduckgo(query, max_results)

    if not urls:
        logger.info("DuckDuckGo returned no results, trying Serper fallback...")
        urls = await search_serper(query, max_results * 2)  # Serper uses different max

    # Random delay to avoid rate limiting
    delay = random.uniform(0.5, 1.5)
    import asyncio
    await asyncio.sleep(delay)

    return urls[:max_results]