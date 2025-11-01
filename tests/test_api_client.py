"""Tests for Harvard Library API client."""

import pytest
import respx
from httpx import Response

from harvard_library_mcp.api.client import HarvardLibraryClient
from harvard_library_mcp.models.harvard_models import HarvardSearchResult


@pytest.fixture
def client():
    """Create a test client instance."""
    return HarvardLibraryClient(
        base_url="https://test-api.lib.harvard.edu/v2",
        rate_limit_requests_per_second=100,  # High rate limit for tests
    )


@pytest.fixture
def mock_search_response():
    """Mock search response data."""
    return {
        "items": {
            "item": [
                {
                    "id": "12345",
                    "titleInfo": {
                        "title": "Test Book Title"
                    },
                    "nameInfo": {
                        "namePart": "Test Author"
                    },
                    "originInfo": {
                        "dateIssued": "2023",
                        "publisher": "Test Publisher"
                    },
                    "language": {
                        "languageTerm": "eng"
                    }
                }
            ]
        },
        "pagination": {
            "numFound": 1,
            "start": 0,
            "rows": 20
        }
    }


@pytest.mark.asyncio
async def test_search_basic(client, mock_search_response):
    """Test basic search functionality."""
    with respx.mock:
        # Mock the API response
        respx.get("https://test-api.lib.harvard.edu/v2/items.json").mock(
            return_value=Response(200, json=mock_search_response)
        )

        # Perform search
        result = await client.search(query="test query", limit=10)

        # Verify results
        assert isinstance(result, HarvardSearchResult)
        assert result.total_count == 1
        assert len(result.records) == 1
        assert result.records[0].title == "Test Book Title"
        assert result.records[0].authors == ["Test Author"]
        assert result.limit == 10


@pytest.mark.asyncio
async def test_search_by_title(client, mock_search_response):
    """Test search by title."""
    with respx.mock:
        respx.get("https://test-api.lib.harvard.edu/v2/items.json").mock(
            return_value=Response(200, json=mock_search_response)
        )

        result = await client.search(title="Test Book Title")
        assert result.total_count == 1
        assert len(result.records) == 1


@pytest.mark.asyncio
async def test_search_with_filters(client):
    """Test search with multiple filters."""
    with respx.mock:
        mock_response = {
            "items": {"item": []},
            "pagination": {"numFound": 0, "start": 0, "rows": 20}
        }
        respx.get("https://test-api.lib.harvard.edu/v2/items.json").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await client.search(
            query="test",
            author="test author",
            subject="test subject",
            collection="test collection",
            language="eng"
        )
        assert result.total_count == 0


@pytest.mark.asyncio
async def test_get_record_by_id(client, mock_search_response):
    """Test getting a specific record by ID."""
    with respx.mock:
        respx.get("https://test-api.lib.harvard.edu/v2/items/12345.json").mock(
            return_value=Response(200, json={"id": "12345", **mock_search_response["items"]["item"][0]})
        )

        record = await client.get_record_by_id("12345")
        assert record is not None
        assert record.id == "12345"
        assert record.title == "Test Book Title"


@pytest.mark.asyncio
async def test_get_nonexistent_record(client):
    """Test getting a non-existent record."""
    with respx.mock:
        respx.get("https://test-api.lib.harvard.edu/v2/items/nonexistent.json").mock(
            return_value=Response(404)
        )

        record = await client.get_record_by_id("nonexistent")
        assert record is None


@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test that rate limiting is working."""
    # This test would need to be more sophisticated to actually test rate limiting
    # For now, we just verify the client has the rate limiter
    assert client.rate_limiter is not None
    assert client.rate_limiter.requests_per_second == 100


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling in API calls."""
    with respx.mock:
        respx.get("https://test-api.lib.harvard.edu/v2/items.json").mock(
            return_value=Response(500, text="Internal Server Error")
        )

        with pytest.raises(Exception):
            await client.search(query="test")


def test_build_url(client):
    """Test URL building functionality."""
    url = client._build_url("items", {"q": "test", "limit": 10})
    assert "items" in url
    assert "q=test" in url
    assert "limit=10" in url


@pytest.mark.asyncio
async def test_xml_response_parsing(client):
    """Test XML response parsing."""
    mock_xml_response = """<?xml version="1.0" encoding="UTF-8"?>
    <items>
        <item>
            <id>12345</id>
            <titleInfo>
                <title>Test Book Title</title>
            </titleInfo>
        </item>
    </items>"""

    with respx.mock:
        respx.get("https://test-api.lib.harvard.edu/v2/items.xml").mock(
            return_value=Response(200, text=mock_xml_response)
        )

        result = await client.search(query="test", response_format="xml")
        assert isinstance(result, HarvardSearchResult)