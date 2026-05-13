"""
Test suite for PDFParser implementation.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from backend.ingestion.parsers.pdf_parser import PDFParser
from backend.ingestion.parsers.base import ParseResult

@pytest.fixture
def pdf_parser():
    """Fixture for PDFParser instance."""
    return PDFParser()

def test_can_parse_pdf(pdf_parser):
    """Test that PDFParser can detect PDF files."""
    assert pdf_parser.can_parse("document.pdf", b"fake_pdf_content")
    assert not pdf_parser.can_parse("document.txt", b"fake_txt_content")

def test_parse_success(pdf_parser):
    """Test successful PDF parsing."""
    # Mock PDF content
    mock_content = b"fake_pdf_content"

    with patch.object(pdf_parser, "_extract_with_pypdf", return_value=ParseResult(
        title="Test Title",
        raw_text="Test raw text",
        sections=[{"title": "Section 1", "content": "Section content", "level": 1}],
        metadata={"parser": "pypdf", "confidence": 0.7}
    )):
        result = pdf_parser.parse("test.pdf", mock_content)
        assert result is not None
        assert result.title == "Test Title"
        assert len(result.sections) == 1

def test_parse_fallback(pdf_parser):
    """Test fallback extraction strategies."""
    mock_content = b"fake_pdf_content"

    # First extractor fails, second succeeds
    with patch.object(pdf_parser, "_extract_with_pypdf", side_effect=Exception("pypdf failed")):
        with patch.object(pdf_parser, "_extract_with_pymupdf", return_value=ParseResult(
            title="Fallback Title",
            raw_text="Fallback raw text",
            sections=[{"title": "Fallback Section", "content": "Fallback content", "level": 1}],
            metadata={"parser": "pymupdf", "confidence": 0.85}
        )):
            result = pdf_parser.parse("test.pdf", mock_content)
            assert result is not None
            assert result.title == "Fallback Title"

def test_extract_title(pdf_parser):
    """Test title extraction from PDF text."""
    test_text = """
    Title: Advanced Machine Learning Techniques
    Abstract: This paper presents new approaches to machine learning...
    """

    title = pdf_parser._extract_title(test_text)
    assert title == "Advanced Machine Learning Techniques"

def test_section_detection(pdf_parser):
    """Test basic section detection."""
    test_text = """
    Introduction to Neural Networks
    This is the introduction section...

    Methods
    We describe our methodology here...

    Results
    Our results are presented below.
    """

    sections = pdf_parser._detect_sections_basic(test_text)
    assert len(sections) == 3
    assert sections[0]["title"] == "Introduction to Neural Networks"
    assert sections[1]["title"] == "Methods"
    assert sections[2]["title"] == "Results"

def test_error_handling(pdf_parser):
    """Test error handling in parsing."""
    mock_content = b"invalid_pdf_content"

    with patch.object(pdf_parser, "_extract_with_pypdf", side_effect=Exception("Invalid PDF")):
        result = pdf_parser.parse("invalid.pdf", mock_content)
        assert result is None