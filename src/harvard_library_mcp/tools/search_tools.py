"""MCP tools for Harvard Library catalog search operations."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from ..api.client import HarvardLibraryClient
from ..models.harvard_models import (
    DateRange,
    GeographicFilter,
    HarvardRecord,
    HarvardSearchResult,
    ModsMetadata,
    SearchParameters,
)

logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[HarvardLibraryClient] = None


async def get_client() -> HarvardLibraryClient:
    """Get or create the Harvard Library API client."""
    global _client
    if _client is None:
        _client = HarvardLibraryClient()
    return _client


async def search_catalog(
    query: str,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog with a general query.

    Args:
        query: General search query string
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results with records, total count, and pagination info
    """
    try:
        client = await get_client()
        result = await client.search(
            query=query,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
            "search_time": result.search_time,
        }

    except Exception as e:
        logger.error(f"Error in search_catalog: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
        }


async def search_by_title(
    title: str,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog by title.

    Args:
        title: Title search query
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        result = await client.search(
            query=title,  # Use title as the query parameter
            title=title,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
        }

    except Exception as e:
        logger.error(f"Error in search_by_title: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
        }


async def search_by_author(
    author: str,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog by author.

    Args:
        author: Author search query
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        result = await client.search(
            query=author,  # Use author as the query parameter
            author=author,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
        }

    except Exception as e:
        logger.error(f"Error in search_by_author: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
        }


async def search_by_subject(
    subject: str,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog by subject.

    Args:
        subject: Subject search query
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        result = await client.search(
            query=subject,  # Use subject as the query parameter
            subject=subject,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
        }

    except Exception as e:
        logger.error(f"Error in search_by_subject: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
        }


async def search_by_collection(
    collection: str,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search within a specific Harvard Library collection.

    Args:
        collection: Collection name or identifier (setName parameter)
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        result = await client.search(
            query=collection,  # Use collection as the query parameter
            collection=collection,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
            "collection": collection,
        }

    except Exception as e:
        logger.error(f"Error in search_by_collection: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
            "collection": collection,
        }


async def search_by_date_range(
    start_date: str,
    end_date: str,
    query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog by publication date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        query: Optional additional search query
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        result = await client.search(
            query=query,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
            "date_range": f"{start_date} to {end_date}",
        }

    except Exception as e:
        logger.error(f"Error in search_by_date_range: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
            "date_range": f"{start_date} to {end_date}",
        }


async def search_by_geographic_origin(
    origin_place: str,
    query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Search the Harvard Library catalog by geographic origin.

    Args:
        origin_place: Geographic origin place for filtering
        query: Optional additional search query
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        # Use origin_place as query if no separate query provided
        search_query = query or origin_place
        result = await client.search(
            query=search_query,
            origin_place=origin_place,
            limit=limit,
            offset=offset,
            response_format=response_format
        )

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
            "origin_place": origin_place,
        }

    except Exception as e:
        logger.error(f"Error in search_by_geographic_origin: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
            "origin_place": origin_place,
        }


async def advanced_search(
    query: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    collection: Optional[str] = None,
    origin_place: Optional[str] = None,
    publication_place: Optional[str] = None,
    language: Optional[str] = None,
    format_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Perform advanced search with multiple filters on the Harvard Library catalog.

    Args:
        query: General search query
        title: Title filter
        author: Author filter
        subject: Subject filter
        collection: Collection filter
        origin_place: Origin place filter
        publication_place: Publication place filter
        language: Language filter
        format_type: Format type filter
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
        sort_by: Sort field
        sort_order: Sort order ('asc' or 'desc')
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing search results
    """
    try:
        client = await get_client()
        # Ensure we have a query parameter - use first available field as query
        search_query = query or title or author or subject or collection or ""
        result = await client.search(
            query=search_query,
            title=title,
            author=author,
            subject=subject,
            collection=collection,
            origin_place=origin_place,
            publication_place=publication_place,
            language=language,
            format_type=format_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            response_format=response_format
        )

        # Build filter summary
        filters = []
        if title:
            filters.append(f"title: {title}")
        if author:
            filters.append(f"author: {author}")
        if subject:
            filters.append(f"subject: {subject}")
        if collection:
            filters.append(f"collection: {collection}")
        if origin_place:
            filters.append(f"origin: {origin_place}")
        if publication_place:
            filters.append(f"pub place: {publication_place}")
        if language:
            filters.append(f"language: {language}")
        if format_type:
            filters.append(f"format: {format_type}")
        if start_date or end_date:
            date_range = f"{start_date or 'earliest'} to {end_date or 'latest'}"
            filters.append(f"date range: {date_range}")

        return {
            "success": True,
            "records": [record.model_dump() for record in result.records],
            "total_count": result.total_count,
            "limit": result.limit,
            "offset": result.offset,
            "has_more": result.has_more,
            "filters": filters,
            "sort": f"{sort_by} {sort_order}" if sort_by else None,
        }

    except Exception as e:
        logger.error(f"Error in advanced_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "records": [],
            "total_count": 0,
        }


async def get_record_details(
    record_id: str,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Get detailed information for a specific Harvard Library catalog record.

    Args:
        record_id: Unique identifier for the record
        response_format: Response format ('json' or 'xml')

    Returns:
        Dictionary containing detailed record information
    """
    try:
        client = await get_client()
        record = await client.get_record_by_id(record_id, response_format)

        if record is None:
            return {
                "success": False,
                "error": f"Record {record_id} not found",
                "record": None,
            }

        return {
            "success": True,
            "record": record.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error in get_record_details: {e}")
        return {
            "success": False,
            "error": str(e),
            "record": None,
        }


async def get_collections_list() -> Dict[str, Any]:
    """
    Get a list of available Harvard Library collections.

    Note: This is a placeholder implementation. The actual Harvard API
    may not have a specific endpoint for listing collections. In practice,
    collections are typically discovered through search results or documentation.

    Returns:
        Dictionary containing collection information
    """
    try:
        # Some known Harvard collections that can be used with the setName parameter
        known_collections = [
            {
                "id": "English_Crime_and_Execution_Broadsides",
                "name": "English Crime and Execution Broadsides",
                "description": "Collection of 18th-19th century English crime broadsides"
            },
            {
                "id": "Harvard_Graduate_School_of_Education",
                "name": "Harvard Graduate School of Education Collection",
                "description": "Materials from the Harvard Graduate School of Education"
            },
            {
                "id": "Women_Working_1800_1930",
                "name": "Women Working, 1800-1930",
                "description": "Collection focusing on women's roles in the economy"
            },
            {
                "id": "Latin_American_Pamphlets",
                "name": "Latin American Pamphlets",
                "description": "Historical pamphlets from Latin America"
            },
            {
                "id": "Harvard_Medical_School",
                "name": "Harvard Medical School Collection",
                "description": "Historical materials from Harvard Medical School"
            },
        ]

        return {
            "success": True,
            "collections": known_collections,
            "note": "This is a curated list of known collections. For a comprehensive list, consult Harvard Library documentation."
        }

    except Exception as e:
        logger.error(f"Error in get_collections_list: {e}")
        return {
            "success": False,
            "error": str(e),
            "collections": [],
        }


async def parse_mods_metadata(
    mods_xml: str
) -> Dict[str, Any]:
    """
    Parse MODS XML metadata and extract structured information.

    Args:
        mods_xml: MODS XML content as string

    Returns:
        Dictionary containing parsed MODS metadata
    """
    try:
        mods_metadata = ModsMetadata.from_xml(mods_xml)

        # Extract commonly needed fields in a simplified format
        simplified = {
            "success": True,
            "parsed_metadata": {
                "title": None,
                "authors": [],
                "publication_date": None,
                "publisher": None,
                "language": None,
                "format": None,
                "subjects": [],
                "description": None,
                "identifiers": {},
                "physical_description": None,
                "classification": [],
            },
            "full_metadata": mods_metadata.model_dump(),
        }

        # Extract simplified information
        if mods_metadata.title_info:
            if isinstance(mods_metadata.title_info, dict):
                title = mods_metadata.title_info.get("title")
                if title:
                    simplified["parsed_metadata"]["title"] = title.get("text", title) if isinstance(title, dict) else str(title)

        if mods_metadata.name_info:
            for name in mods_metadata.name_info:
                if isinstance(name, dict):
                    name_parts = name.get("namePart")
                    if name_parts:
                        if isinstance(name_parts, list):
                            simplified["parsed_metadata"]["authors"].extend(
                                str(part.get("text", part) if isinstance(part, dict) else part)
                                for part in name_parts
                            )
                        else:
                            simplified["parsed_metadata"]["authors"].append(
                                str(name_parts.get("text", name_parts) if isinstance(name_parts, dict) else name_parts)
                            )

        if mods_metadata.origin_info:
            origin = mods_metadata.origin_info
            if isinstance(origin, dict):
                # Publication date
                date_issued = origin.get("dateIssued")
                if date_issued:
                    simplified["parsed_metadata"]["publication_date"] = (
                        date_issued.get("text", date_issued) if isinstance(date_issued, dict) else str(date_issued)
                    )

                # Publisher
                publisher = origin.get("publisher")
                if publisher:
                    simplified["parsed_metadata"]["publisher"] = (
                        publisher.get("text", publisher) if isinstance(publisher, dict) else str(publisher)
                    )

        if mods_metadata.language:
            language = mods_metadata.language
            if isinstance(language, dict):
                lang_term = language.get("languageTerm")
                if lang_term:
                    simplified["parsed_metadata"]["language"] = (
                        lang_term.get("text", lang_term) if isinstance(lang_term, dict) else str(lang_term)
                    )

        if mods_metadata.physical_description:
            phys_desc = mods_metadata.physical_description
            if isinstance(phys_desc, dict):
                form = phys_desc.get("form")
                if form:
                    simplified["parsed_metadata"]["format"] = (
                        form.get("text", form) if isinstance(form, dict) else str(form)
                    )

        if mods_metadata.subjects:
            for subject in mods_metadata.subjects:
                if isinstance(subject, dict):
                    topic = subject.get("topic")
                    if topic:
                        if isinstance(topic, list):
                            simplified["parsed_metadata"]["subjects"].extend(
                                str(t.get("text", t) if isinstance(t, dict) else t) for t in topic
                            )
                        else:
                            simplified["parsed_metadata"]["subjects"].append(
                                str(topic.get("text", topic) if isinstance(topic, dict) else topic)
                            )

        if mods_metadata.classification:
            classifications = []
            for classification in mods_metadata.classification:
                if isinstance(classification, dict):
                    class_value = classification.get("text", classification)
                    if class_value:
                        classifications.append(str(class_value))
            simplified["parsed_metadata"]["classification"] = classifications

        return simplified

    except Exception as e:
        logger.error(f"Error parsing MODS metadata: {e}")
        return {
            "success": False,
            "error": str(e),
            "parsed_metadata": None,
            "full_metadata": None,
        }