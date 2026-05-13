"""
Test suite for ParserRegistry implementation.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.ingestion.parsers.registry import ParserRegistry
from backend.ingestion.parsers.base import DocumentParser, ParseResult

@pytest.fixture
def parser_registry():
    """Fixture for ParserRegistry instance."""
    return ParserRegistry()

def test_register_parsers(parser_registry):
    """Test parser registration."""
    mock_parser = MagicMock(spec=DocumentParser)
    mock_parser.can_parse.return_value = True

    parser_registry.register(mock_parser)
    assert len(parser_registry._parsers) == 4  # 4 built-in parsers (Markdown, Txt, PDF, DOCX) + 1 registered

def test_get_parser(parser_registry):
    """Test parser lookup."""
    mock_parser = MagicMock(spec=DocumentParser)
    mock_parser.can_parse.return_value = True

    parser_registry.register(mock_parser)

    # Test that the parser is found
    result = parser_registry.get_parser("test.pdf", b"fake_content")
    assert result is not None

    # Test that no parser is found for unknown type
    with patch.object(parser_registry, '_parsers', []):
        result = parser_registry.get_parser("unknown.unknown", b"fake_content")
        assert result is None

def test_parse_document(parser_registry):
    """Test document parsing through registry."""
    mock_parser = MagicMock(spec=DocumentParser)
    mock_parser.can_parse.return_value = True
    mock_parser.parse.return_value = ParseResult(
        title="Test Title",
        raw_text="Test raw text",
        sections=[{"title": "Section 1", "content": "Section content", "level": 1}],
        metadata={"parser": "test_parser", "confidence": 0.9}
    )

    parser_registry.register(mock_parser)

    result = parser_registry.parse("test.pdf", b"fake_content")
    assert result is not None
    assert result.title == "Test Title"

def test_parse_failure(parser_registry):
    """Test parsing failure when no parser is found."""
    with patch.object(parser_registry, '_parsers', []):
        result = parser_registry.parse("unknown.unknown", b"fake_content")
        assert result is None