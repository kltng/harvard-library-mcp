"""Pydantic models for Harvard Library API data structures."""

from datetime import date
from typing import Any, Dict, List, Optional, Union
from xml.etree import ElementTree

from pydantic import BaseModel, Field, HttpUrl


class DateRange(BaseModel):
    """Date range for filtering searches."""

    start_date: Optional[Union[date, str]] = Field(
        default=None,
        description="Start date for date range filter (YYYY-MM-DD format or date object)"
    )
    end_date: Optional[Union[date, str]] = Field(
        default=None,
        description="End date for date range filter (YYYY-MM-DD format or date object)"
    )


class GeographicFilter(BaseModel):
    """Geographic origin filter for searches."""

    origin_place: Optional[str] = Field(
        default=None,
        description="Geographic origin place for filtering"
    )
    publication_place: Optional[str] = Field(
        default=None,
        description="Publication place for filtering"
    )


class SearchParameters(BaseModel):
    """Parameters for catalog searches."""

    query: str = Field(..., description="Search query string")
    title: Optional[str] = Field(default=None, description="Title filter")
    author: Optional[str] = Field(default=None, description="Author filter")
    subject: Optional[str] = Field(default=None, description="Subject filter")
    collection: Optional[str] = Field(default=None, description="Collection filter")
    date_range: Optional[DateRange] = Field(default=None, description="Date range filter")
    geographic_filter: Optional[GeographicFilter] = Field(
        default=None,
        description="Geographic filter"
    )
    language: Optional[str] = Field(default=None, description="Language filter")
    format: Optional[str] = Field(default=None, description="Format type filter")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Results offset for pagination")
    sort_by: Optional[str] = Field(
        default=None,
        description="Sort field (e.g., 'title', 'author', 'date')"
    )
    sort_order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order ('asc' or 'desc')"
    )


class ModsMetadata(BaseModel):
    """MODS (Metadata Object Description Schema) metadata structure."""

    title_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Title information from MODS"
    )
    name_info: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Author/creator information from MODS"
    )
    origin_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Publication origin information"
    )
    language: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Language information"
    )
    physical_description: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Physical description (extent, format, etc.)"
    )
    subjects: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Subject headings"
    )
    classification: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Classification numbers (LC, Dewey, etc.)"
    )
    related_items: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Related items information"
    )
    identifiers: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Various identifiers (ISBN, ISSN, OCLC, etc.)"
    )
    locations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Holdings and location information"
    )
    record_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Record information (creation, modification dates)"
    )
    extensions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Harvard-specific extensions (stackscore, etc.)"
    )
    raw_xml: Optional[str] = Field(
        default=None,
        description="Raw MODS XML content"
    )

    @classmethod
    def from_xml(cls, xml_content: str) -> "ModsMetadata":
        """Create ModsMetadata from XML content."""
        try:
            root = ElementTree.fromstring(xml_content)

            # Extract MODS namespaces
            namespaces = {
                'mods': 'http://www.loc.gov/mods/v3',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }

            def extract_field(tag: str) -> Any:
                """Extract field from XML, handling multiple occurrences."""
                elements = root.findall(f'.//mods:{tag}', namespaces)
                if not elements:
                    return None

                if len(elements) == 1:
                    return element_to_dict(elements[0])

                return [element_to_dict(elem) for elem in elements]

            def element_to_dict(element: ElementTree.Element) -> Dict[str, Any]:
                """Convert XML element to dictionary representation."""
                result = {}

                # Add attributes
                if element.attrib:
                    result.update(element.attrib)

                # Add text content
                if element.text and element.text.strip():
                    result['text'] = element.text.strip()

                # Add child elements
                for child in element:
                    child_data = element_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data

                return result

            return cls(
                title_info=extract_field('titleInfo'),
                name_info=extract_field('name'),
                origin_info=extract_field('originInfo'),
                language=extract_field('language'),
                physical_description=extract_field('physicalDescription'),
                subjects=extract_field('subject'),
                classification=extract_field('classification'),
                related_items=extract_field('relatedItem'),
                identifiers=extract_field('identifier'),
                locations=extract_field('location'),
                record_info=extract_field('recordInfo'),
                raw_xml=xml_content
            )

        except Exception as e:
            # Return minimal metadata if parsing fails
            return cls(raw_xml=xml_content)

    @classmethod
    def from_mods_dict(cls, mods_data: Dict[str, Any]) -> "ModsMetadata":
        """Create ModsMetadata from a dictionary representation of MODS data."""
        try:
            return cls(
                title_info=mods_data.get("titleInfo"),
                name_info=mods_data.get("name") if isinstance(mods_data.get("name"), list) else [mods_data.get("name")] if mods_data.get("name") else None,
                origin_info=mods_data.get("originInfo"),
                language=mods_data.get("language"),
                physical_description=mods_data.get("physicalDescription"),
                subjects=mods_data.get("subject") if isinstance(mods_data.get("subject"), list) else [mods_data.get("subject")] if mods_data.get("subject") else None,
                classification=mods_data.get("classification") if isinstance(mods_data.get("classification"), list) else [mods_data.get("classification")] if mods_data.get("classification") else None,
                related_items=mods_data.get("relatedItem") if isinstance(mods_data.get("relatedItem"), list) else [mods_data.get("relatedItem")] if mods_data.get("relatedItem") else None,
                identifiers=mods_data.get("identifier") if isinstance(mods_data.get("identifier"), list) else [mods_data.get("identifier")] if mods_data.get("identifier") else None,
                locations=mods_data.get("location"),
                record_info=mods_data.get("recordInfo"),
                extensions=mods_data.get("extension"),
                raw_xml=str(mods_data)  # Store string representation
            )
        except Exception as e:
            # Return minimal metadata if parsing fails
            return cls(raw_xml=str(mods_data))


class HarvardRecord(BaseModel):
    """A single Harvard Library catalog record."""

    id: str = Field(..., description="Unique identifier for the record")
    title: Optional[str] = Field(default=None, description="Title of the work")
    authors: Optional[List[str]] = Field(
        default=None,
        description="List of authors/creators"
    )
    publication_date: Optional[str] = Field(
        default=None,
        description="Publication date"
    )
    publisher: Optional[str] = Field(default=None, description="Publisher name")
    language: Optional[str] = Field(default=None, description="Language code")
    format_type: Optional[str] = Field(default=None, description="Format type")
    subjects: Optional[List[str]] = Field(
        default=None,
        description="Subject headings"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description or abstract"
    )
    identifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Various identifiers (ISBN, ISSN, OCLC, etc.)"
    )
    holdings: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Library holdings information"
    )
    classification: Optional[List[str]] = Field(
        default=None,
        description="Classification numbers"
    )
    collections: Optional[List[str]] = Field(
        default=None,
        description="Collections this record belongs to"
    )
    stackscore: Optional[float] = Field(
        default=None,
        description="Harvard-specific stackscore metric"
    )
    digital_content: Optional[bool] = Field(
        default=False,
        description="Whether digital content is available"
    )
    mods_metadata: Optional[ModsMetadata] = Field(
        default=None,
        description="Complete MODS metadata"
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw API response data"
    )


class HarvardCollection(BaseModel):
    """Harvard Library collection information."""

    id: str = Field(..., description="Collection identifier")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(
        default=None,
        description="Collection description"
    )
    record_count: Optional[int] = Field(
        default=None,
        description="Number of records in collection"
    )
    curator: Optional[str] = Field(default=None, description="Collection curator")
    access_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to access collection"
    )


class HarvardSearchResult(BaseModel):
    """Results from a Harvard Library catalog search."""

    records: List[HarvardRecord] = Field(
        default_factory=list,
        description="List of catalog records"
    )
    total_count: int = Field(default=0, description="Total number of results")
    limit: int = Field(default=20, description="Number of results per page")
    offset: int = Field(default=0, description="Results offset")
    has_more: bool = Field(default=False, description="Whether more results are available")
    search_time: Optional[float] = Field(
        default=None,
        description="Search execution time in seconds"
    )
    facets: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Search facets for filtering"
    )
    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Search suggestions"
    )
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw API response data"
    )