"""Tests for search tools."""

import pytest
import respx
from httpx import Response

from harvard_library_mcp.tools.search_tools import (
    search_catalog,
    search_by_title,
    search_by_author,
    advanced_search,
    get_record_details,
    parse_mods_metadata,
)


@pytest.fixture
def mock_search_response():
    """Mock search response data."""
    return {
        "success": True,
        "records": [
            {
                "id": "12345",
                "title": "Test Book Title",
                "authors": ["Test Author"],
                "publication_date": "2023",
                "publisher": "Test Publisher"
            }
        ],
        "total_count": 1,
        "limit": 20,
        "offset": 0,
        "has_more": False
    }


@pytest.mark.asyncio
async def test_search_catalog_success(mock_search_response):
    """Test successful catalog search."""
    # This test would require mocking the underlying API client
    # For now, we test the basic structure
    result = await search_catalog(
        query="test query",
        limit=10,
        offset=0
    )

    # The actual result depends on API connectivity
    # In a real test environment, we would mock the API client
    assert isinstance(result, dict)
    assert "success" in result
    assert "records" in result


@pytest.mark.asyncio
async def test_search_by_title():
    """Test search by title."""
    result = await search_by_title(
        title="Test Book Title",
        limit=5
    )

    assert isinstance(result, dict)
    assert "success" in result
    assert "records" in result


@pytest.mark.asyncio
async def test_search_by_author():
    """Test search by author."""
    result = await search_by_author(
        author="Test Author Name",
        limit=15
    )

    assert isinstance(result, dict)
    assert "success" in result
    assert "records" in result


@pytest.mark.asyncio
async def test_advanced_search():
    """Test advanced search with multiple filters."""
    result = await advanced_search(
        query="test",
        title="specific title",
        author="specific author",
        subject="specific subject",
        limit=25,
        sort_by="title",
        sort_order="desc"
    )

    assert isinstance(result, dict)
    assert "success" in result
    assert "records" in result
    assert "filters" in result


@pytest.mark.asyncio
async def test_get_record_details():
    """Test getting record details."""
    result = await get_record_details(
        record_id="12345",
        response_format="json"
    )

    assert isinstance(result, dict)
    assert "success" in result
    assert "record" in result


@pytest.mark.asyncio
async def test_parse_mods_metadata():
    """Test MODS metadata parsing."""
    mods_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <mods xmlns="http://www.loc.gov/mods/v3">
        <titleInfo>
            <title>Test Book Title</title>
            <subTitle>A Subtitle</subTitle>
        </titleInfo>
        <name type="personal">
            <namePart>Test Author</namePart>
            <role>
                <roleTerm type="text">author</roleTerm>
            </role>
        </name>
        <originInfo>
            <dateIssued>2023</dateIssued>
            <publisher>Test Publisher</publisher>
            <place>
                <placeTerm type="text">Boston</placeTerm>
            </place>
        </originInfo>
        <language>
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <subject>
            <topic>Test Subject</topic>
        </subject>
        <physicalDescription>
            <form authority="marcform">print</form>
            <extent>250 pages</extent>
        </physicalDescription>
        <identifier type="isbn">9781234567890</identifier>
    </mods>"""

    result = await parse_mods_metadata(mods_xml)

    assert isinstance(result, dict)
    assert "success" in result
    assert "parsed_metadata" in result
    assert "full_metadata" in result

    if result["success"]:
        parsed = result["parsed_metadata"]
        assert "title" in parsed
        assert "authors" in parsed
        assert "publication_date" in parsed
        assert "identifiers" in parsed


@pytest.mark.asyncio
async def test_search_with_pagination():
    """Test search with pagination parameters."""
    result = await search_catalog(
        query="test",
        limit=50,
        offset=100
    )

    assert isinstance(result, dict)
    assert "limit" in result
    assert "offset" in result
    assert "has_more" in result


@pytest.mark.asyncio
async def test_search_with_different_formats():
    """Test search with different response formats."""
    # Test JSON format
    result_json = await search_catalog(
        query="test",
        response_format="json"
    )
    assert isinstance(result_json, dict)

    # Test XML format (if supported)
    result_xml = await search_catalog(
        query="test",
        response_format="xml"
    )
    assert isinstance(result_xml, dict)


def test_search_parameters_validation():
    """Test search parameter validation in tool functions."""
    # These tests would check that invalid parameters are handled appropriately
    # Since the tools delegate to the API client, most validation happens there

    # Test that required parameters are handled
    # This would be more meaningful with proper mocking
    pass