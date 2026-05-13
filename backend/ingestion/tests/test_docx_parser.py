"""
Test suite for DOCXParser implementation.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.ingestion.parsers.docx_parser import DOCXParser
from backend.ingestion.parsers.base import ParseResult
from docx import Document

@pytest.fixture
def docx_parser():
    """Fixture for DOCXParser instance."""
    return DOCXParser()

def test_can_parse_docx(docx_parser):
    """Test that DOCXParser can detect DOCX files."""
    assert docx_parser.can_parse("document.docx", b"fake_docx_content")
    assert not docx_parser.can_parse("document.pdf", b"fake_pdf_content")

def test_parse_success(docx_parser):
    """Test successful DOCX parsing."""
    mock_core_properties = MagicMock()
    mock_core_properties.title = "Test Document"
    mock_doc = MagicMock(spec=Document)
    mock_doc.core_properties = mock_core_properties
    mock_doc.paragraphs = [
        MagicMock(text="This is a test paragraph"),
        MagicMock(text="Another paragraph", style=MagicMock(name="Heading 1"))
    ]

    with patch('backend.ingestion.parsers.docx_parser.Document', return_value=mock_doc):
        result = docx_parser.parse("test.docx", b"fake_docx_content")
        assert result is not None
        assert result.title == "Test Document"
        assert len(result.sections) == 1

def test_parse_error_handling(docx_parser):
    """Test error handling in parsing."""
    with patch('backend.ingestion.parsers.docx_parser.Document', side_effect=Exception("Invalid DOCX")):
        result = docx_parser.parse("invalid.docx", b"invalid_content")
        assert result is None

def test_heading_detection_integration(docx_parser):
    """Test heading detection in DOCX parsing."""
    mock_core_properties = MagicMock()
    mock_core_properties.title = "Test Document"
    mock_doc = MagicMock(spec=Document)
    mock_doc.core_properties = mock_core_properties
    mock_doc.paragraphs = [
        MagicMock(text="Introduction", style=MagicMock(name="Heading 1")),
        MagicMock(text="This is the introduction content"),
        MagicMock(text="Methods", style=MagicMock(name="Heading 2")),
        MagicMock(text="We describe our methods here")
    ]

    with patch('backend.ingestion.parsers.docx_parser.Document', return_value=mock_doc):
        result = docx_parser.parse("test.docx", b"fake_docx_content")
        assert result is not None
        assert result.title == "Test Document"
        assert len(result.sections) == 2
        assert result.sections[0]["title"] == "Introduction"
        assert result.sections[1]["title"] == "Methods"