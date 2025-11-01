"""Tests for data models."""

import pytest
from datetime import date

from harvard_library_mcp.models.harvard_models import (
    DateRange,
    GeographicFilter,
    HarvardRecord,
    HarvardSearchResult,
    ModsMetadata,
    SearchParameters,
)


def test_date_range_model():
    """Test DateRange model."""
    # Test with dates
    date_range = DateRange(
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
    assert date_range.start_date == "2023-01-01"
    assert date_range.end_date == "2023-12-31"

    # Test with date objects
    date_range_objs = DateRange(
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )
    assert date_range_objs.start_date == date(2023, 1, 1)
    assert date_range_objs.end_date == date(2023, 12, 31)


def test_geographic_filter_model():
    """Test GeographicFilter model."""
    geo_filter = GeographicFilter(
        origin_place="Boston",
        publication_place="Cambridge"
    )
    assert geo_filter.origin_place == "Boston"
    assert geo_filter.publication_place == "Cambridge"


def test_search_parameters_model():
    """Test SearchParameters model."""
    params = SearchParameters(
        query="test query",
        title="test title",
        author="test author",
        limit=50,
        offset=10
    )
    assert params.query == "test query"
    assert params.title == "test title"
    assert params.author == "test author"
    assert params.limit == 50
    assert params.offset == 10
    assert params.sort_order == "asc"  # Default value


def test_harvard_record_model():
    """Test HarvardRecord model."""
    record = HarvardRecord(
        id="12345",
        title="Test Book",
        authors=["Author One", "Author Two"],
        publication_date="2023",
        publisher="Test Publisher",
        language="eng",
        subjects=["Subject 1", "Subject 2"],
        identifiers={"ISBN": "9781234567890"}
    )
    assert record.id == "12345"
    assert record.title == "Test Book"
    assert len(record.authors) == 2
    assert record.publication_date == "2023"
    assert "ISBN" in record.identifiers


def test_harvard_search_result_model():
    """Test HarvardSearchResult model."""
    record1 = HarvardRecord(id="1", title="Book 1")
    record2 = HarvardRecord(id="2", title="Book 2")

    result = HarvardSearchResult(
        records=[record1, record2],
        total_count=100,
        limit=20,
        offset=0,
        has_more=True
    )
    assert len(result.records) == 2
    assert result.total_count == 100
    assert result.has_more is True


def test_mods_metadata_from_xml():
    """Test ModsMetadata XML parsing."""
    mods_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <mods xmlns="http://www.loc.gov/mods/v3">
        <titleInfo>
            <title>Test Book Title</title>
        </titleInfo>
        <name type="personal">
            <namePart>Test Author</namePart>
        </name>
        <originInfo>
            <dateIssued>2023</dateIssued>
            <publisher>Test Publisher</publisher>
        </originInfo>
        <language>
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <subject>
            <topic>Test Subject</topic>
        </subject>
    </mods>"""

    mods_metadata = ModsMetadata.from_xml(mods_xml)
    assert mods_metadata.raw_xml == mods_xml
    # Note: The actual parsing depends on the XML structure and might need adjustment


def test_mods_metadata_model():
    """Test ModsMetadata model with manual data."""
    metadata = ModsMetadata(
        title_info={"title": "Test Book"},
        name_info=[{"namePart": "Test Author"}],
        raw_xml="<mods>...</mods>"
    )
    assert metadata.title_info["title"] == "Test Book"
    assert metadata.raw_xml == "<mods>...</mods>"


def test_search_parameters_validation():
    """Test SearchParameters validation."""
    # Valid parameters
    params = SearchParameters(
        query="test",
        limit=10,
        sort_order="asc"
    )
    assert params.sort_order == "asc"

    # Invalid sort order should raise exception
    with pytest.raises(ValueError):
        SearchParameters(query="test", sort_order="invalid")

    # Invalid limit should raise exception
    with pytest.raises(ValueError):
        SearchParameters(query="test", limit=0)

    with pytest.raises(ValueError):
        SearchParameters(query="test", limit=101)