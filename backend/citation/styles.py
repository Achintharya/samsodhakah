"""
Citation style formatters — IEEE, ACM, APA, Springer.
"""

from __future__ import annotations

import logging
from typing import Optional
from backend.models.citation import CitationStyle

logger = logging.getLogger(__name__)


def format_citation(citation: dict, style: CitationStyle) -> str:
    """
    Format a citation in the specified style.

    Args:
        citation: Dict with authors, title, year, journal, volume, pages, doi, publisher.
        style: Target citation style.

    Returns:
        Formatted citation string.
    """
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    year = citation.get("year", "n.d.")
    journal = citation.get("journal", "")
    volume = citation.get("volume", "")
    issue = citation.get("issue", "")
    pages = citation.get("pages", "")
    doi = citation.get("doi", "")
    publisher = citation.get("publisher", "")

    if style == CitationStyle.IEEE:
        return _format_ieee(authors, title, year, journal, volume, issue, pages, doi)
    elif style == CitationStyle.ACM:
        return _format_acm(authors, title, year, journal, volume, pages, doi, publisher)
    elif style == CitationStyle.APA:
        return _format_apa(authors, title, year, journal, volume, issue, pages, doi, publisher)
    elif style == CitationStyle.SPRINGER:
        return _format_springer(authors, title, year, journal, volume, pages, doi)
    return _format_ieee(authors, title, year, journal, volume, issue, pages, doi)


def _format_ieee(
    authors: list[str], title: str, year: str | int,
    journal: str, volume: str, issue: str, pages: str, doi: str,
) -> str:
    author_str = ", ".join(authors) if authors else "Unknown"
    parts = [f"{author_str}, \"{title},\""]
    if journal:
        parts.append(f" {journal}")
    if volume:
        vol_str = f" vol. {volume}"
        if issue:
            vol_str += f", no. {issue}"
        parts.append(vol_str)
    if pages:
        parts.append(f", pp. {pages}")
    parts.append(f", {year}.")
    if doi:
        parts.append(f" doi: {doi}.")
    return "".join(parts)


def _format_acm(
    authors: list[str], title: str, year: str | int,
    journal: str, volume: str, pages: str, doi: str, publisher: str,
) -> str:
    author_str = ", ".join(authors) if authors else "Unknown"
    parts = [f"{author_str}. {year}. {title}."]
    if journal:
        parts.append(f" {journal},")
    if volume:
        parts.append(f" {volume},")
    if pages:
        parts.append(f" {pages}.")
    if doi:
        parts.append(f" https://doi.org/{doi}")
    return " ".join(parts)


def _format_apa(
    authors: list[str], title: str, year: str | int,
    journal: str, volume: str, issue: str, pages: str, doi: str, publisher: str,
) -> str:
    if not authors:
        author_str = "Unknown"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    else:
        author_str = f"{authors[0]} et al."

    parts = [f"{author_str} ({year})."]
    parts.append(f" {title}.")
    if journal:
        parts.append(f" *{journal}*,")
    if volume:
        vol_str = f" *{volume}*"
        if issue:
            vol_str += f"({issue})"
        parts.append(vol_str)
    if pages:
        parts.append(f", {pages}.")
    if doi:
        parts.append(f" https://doi.org/{doi}")
    return " ".join(parts)


def _format_springer(
    authors: list[str], title: str, year: str | int,
    journal: str, volume: str, pages: str, doi: str,
) -> str:
    author_str = ", ".join(authors) if authors else "Unknown"
    parts = [f"{author_str}: {title}"]
    if journal:
        parts.append(f", {journal}")
    if volume:
        parts.append(f" {volume}")
    if pages:
        parts.append(f", {pages}")
    parts.append(f" ({year})")
    if doi:
        parts.append(f" doi: {doi}")
    return "".join(parts)