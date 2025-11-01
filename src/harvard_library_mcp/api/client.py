"""Harvard Library API client."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode, urljoin

import httpx
from pydantic import ValidationError

from ..config import settings
from ..models.harvard_models import (
    HarvardRecord,
    HarvardSearchResult,
    ModsMetadata,
    SearchParameters,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, requests_per_second: int = 10, burst_size: int = 20):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token from the rate limiter."""
        async with self._lock:
            now = datetime.now()
            time_passed = (now - self.last_update).total_seconds()

            # Add tokens based on time passed
            self.tokens = min(
                self.burst_size,
                self.tokens + time_passed * self.requests_per_second
            )
            self.last_update = now

            if self.tokens < 1:
                # Need to wait for a token
                wait_time = (1 - self.tokens) / self.requests_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class HarvardLibraryClient:
    """Client for Harvard Library API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        rate_limit_requests_per_second: Optional[int] = None,
    ):
        """
        Initialize Harvard Library API client.

        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
            rate_limit_requests_per_second: Rate limit for requests
        """
        self.base_url = base_url or settings.harvard_api_base_url
        self.timeout = timeout or settings.harvard_api_timeout
        self.user_agent = user_agent or settings.harvard_api_user_agent
        self.rate_limiter = RateLimiter(
            requests_per_second=rate_limit_requests_per_second or settings.rate_limit_requests_per_second,
            burst_size=settings.rate_limit_burst_size
        )

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json,application/xml",
                "Accept-Encoding": "gzip, deflate",
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build complete URL with query parameters."""
        url = urljoin(self.base_url, endpoint)
        if params:
            # Filter out None values and encode parameters
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                query_string = urlencode(filtered_params)
                url = f"{url}?{query_string}"
        return url

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make HTTP request with rate limiting and error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            HTTP response object

        Raises:
            httpx.HTTPError: If request fails
        """
        await self.rate_limiter.acquire()

        url = self._build_url(endpoint, params)
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            logger.debug(f"Making {method} request to {url}")
            response = await self.client.request(
                method=method,
                url=url,
                headers=request_headers,
            )
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request: {e}")
            raise

    async def _parse_xml_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse XML response from Harvard API."""
        try:
            import xmltodict
            content = response.text
            return xmltodict.parse(content)
        except Exception as e:
            logger.error(f"Error parsing XML response: {e}")
            # Return minimal structure if parsing fails
            return {"error": "XML parsing failed", "raw_content": response.text}

    async def _extract_records_from_response(
        self,
        response_data: Dict[str, Any],
        format_type: str = "json"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extract records and total count from API response.

        Args:
            response_data: Parsed response data
            format_type: Response format ('json' or 'xml')

        Returns:
            Tuple of (records list, total count)
        """
        records = []
        total_count = 0

        try:
            if format_type == "json":
                # Handle JSON response format
                if "items" in response_data:
                    items = response_data["items"]
                    if isinstance(items, dict) and "item" in items:
                        records = items["item"] if isinstance(items["item"], list) else [items["item"]]
                    elif isinstance(items, list):
                        records = items

                # Extract pagination info
                pagination = response_data.get("pagination", {})
                if "numFound" in pagination:
                    total_count = int(pagination["numFound"])
                elif "total" in pagination:
                    total_count = int(pagination["total"])

            elif format_type == "xml":
                # Handle XML response format
                if "items" in response_data:
                    items_data = response_data["items"]
                    if "item" in items_data:
                        records = items_data["item"]
                        if not isinstance(records, list):
                            records = [records]

                # Look for pagination info in various possible locations
                for key in ["numFound", "total", "totalResults"]:
                    if key in response_data.get("pagination", {}):
                        total_count = int(response_data["pagination"][key])
                        break
                    elif key in response_data:
                        total_count = int(response_data[key])
                        break

        except Exception as e:
            logger.error(f"Error extracting records from response: {e}")

        return records, total_count

    async def search(
        self,
        query: str,
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
        response_format: str = "json",
    ) -> HarvardSearchResult:
        """
        Search the Harvard Library catalog.

        Args:
            query: General search query
            title: Title filter
            author: Author filter
            subject: Subject filter
            collection: Collection filter (setName parameter)
            origin_place: Origin place filter
            publication_place: Publication place filter
            language: Language filter
            format_type: Format type filter
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD)
            limit: Maximum number of results
            offset: Results offset for pagination
            sort_by: Sort field
            sort_order: Sort order ('asc' or 'desc')
            response_format: Response format ('json' or 'xml')

        Returns:
            HarvardSearchResult object
        """
        # Build query parameters
        params = {
            "limit": limit,
            "start": offset,
        }

        # Add search parameters
        if query:
            params["q"] = query
        if title:
            params["title"] = title
        if author:
            params["author"] = author
        if subject:
            params["subject"] = subject
        if collection:
            params["setName"] = collection
        if origin_place:
            params["originPlace"] = origin_place
        if publication_place:
            params["pubPlace"] = publication_place
        if language:
            params["language"] = language
        if format_type:
            params["resourceType"] = format_type

        # Date range handling
        if start_date and end_date:
            params["dateRange"] = f"{start_date}-{end_date}"
        elif start_date:
            params["date"] = start_date
        elif end_date:
            params["date"] = end_date

        # Sorting
        if sort_by:
            params["sort"] = sort_by
            if sort_order == "desc":
                params["sortDirection"] = "descending"

        # Determine endpoint based on format
        endpoint = "items"
        if response_format == "xml":
            endpoint = "items.xml"
        else:
            endpoint = "items.json"

        try:
            # Make API request
            response = await self._make_request("GET", endpoint, params)

            # Parse response
            if response_format == "xml":
                response_data = await self._parse_xml_response(response)
            else:
                response_data = response.json()

            # Extract records and metadata
            records_data, total_count = await self._extract_records_from_response(
                response_data, response_format
            )

            # Convert to HarvardRecord objects
            records = []
            for record_data in records_data:
                try:
                    record = await self._parse_harvard_record(record_data, response_format)
                    records.append(record)
                except Exception as e:
                    logger.error(f"Error parsing record: {e}")
                    continue

            return HarvardSearchResult(
                records=records,
                total_count=total_count,
                limit=limit,
                offset=offset,
                has_more=(offset + limit) < total_count,
                raw_response=response_data,
            )

        except Exception as e:
            logger.error(f"Search request failed: {e}")
            raise

    async def get_record_by_id(
        self,
        record_id: str,
        response_format: str = "json"
    ) -> Optional[HarvardRecord]:
        """
        Get a specific record by its ID.

        Args:
            record_id: Unique identifier for the record
            response_format: Response format ('json' or 'xml')

        Returns:
            HarvardRecord object or None if not found
        """
        endpoint = f"items/{record_id}"
        if response_format == "xml":
            endpoint = f"items/{record_id}.xml"
        else:
            endpoint = f"items/{record_id}.json"

        try:
            response = await self._make_request("GET", endpoint)

            if response_format == "xml":
                response_data = await self._parse_xml_response(response)
            else:
                response_data = response.json()

            # Extract record data (for single record responses)
            record_data = response_data
            if "items" in response_data and "item" in response_data["items"]:
                record_data = response_data["items"]["item"]
                if isinstance(record_data, list) and record_data:
                    record_data = record_data[0]

            return await self._parse_harvard_record(record_data, response_format)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"Record {record_id} not found")
                return None
            raise
        except Exception as e:
            logger.error(f"Error fetching record {record_id}: {e}")
            raise

    async def _parse_harvard_record(
        self,
        record_data: Dict[str, Any],
        format_type: str = "json"
    ) -> HarvardRecord:
        """Parse Harvard record data into HarvardRecord object."""
        try:
            # Extract basic fields
            record_id = (
                record_data.get("id") or
                record_data.get("@id") or
                record_data.get("recordId", "")
            )

            # Extract title
            title = self._extract_title(record_data, format_type)

            # Extract authors
            authors = self._extract_authors(record_data, format_type)

            # Extract publication date
            pub_date = self._extract_publication_date(record_data, format_type)

            # Extract publisher
            publisher = self._extract_publisher(record_data, format_type)

            # Extract language
            language = self._extract_language(record_data, format_type)

            # Extract format type
            format_type_field = self._extract_format_type(record_data, format_type)

            # Extract subjects
            subjects = self._extract_subjects(record_data, format_type)

            # Extract description
            description = self._extract_description(record_data, format_type)

            # Extract identifiers
            identifiers = self._extract_identifiers(record_data, format_type)

            # Extract holdings
            holdings = self._extract_holdings(record_data, format_type)

            # Extract classification
            classification = self._extract_classification(record_data, format_type)

            # Extract collections
            collections = self._extract_collections(record_data, format_type)

            # Extract stackscore
            stackscore = self._extract_stackscore(record_data, format_type)

            # Extract digital content availability
            digital_content = self._extract_digital_content(record_data, format_type)

            # Parse MODS metadata if available
            mods_metadata = None
            if format_type == "xml" and "mods" in record_data:
                mods_metadata = ModsMetadata.from_xml(str(record_data["mods"]))

            return HarvardRecord(
                id=record_id,
                title=title,
                authors=authors,
                publication_date=pub_date,
                publisher=publisher,
                language=language,
                format_type=format_type_field,
                subjects=subjects,
                description=description,
                identifiers=identifiers,
                holdings=holdings,
                classification=classification,
                collections=collections,
                stackscore=stackscore,
                digital_content=digital_content,
                mods_metadata=mods_metadata,
                raw_data=record_data,
            )

        except Exception as e:
            logger.error(f"Error parsing Harvard record: {e}")
            # Return minimal record if parsing fails
            return HarvardRecord(
                id=str(record_data.get("id", "unknown")),
                raw_data=record_data,
            )

    def _extract_title(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract title from record data."""
        # Try various possible title fields
        title_fields = [
            "titleInfo/title",
            "title",
            "Title",
            "mods/titleInfo/title",
        ]

        for field in title_fields:
            value = self._get_nested_value(data, field)
            if value and isinstance(value, str):
                return value.strip()
            elif isinstance(value, dict) and "text" in value:
                return value["text"].strip()

        return None

    def _extract_authors(self, data: Dict[str, Any], format_type: str) -> Optional[List[str]]:
        """Extract authors from record data."""
        authors = []

        # Try various possible author fields
        author_fields = [
            "nameInfo/namePart",
            "author",
            "Author",
            "creator",
            "Creator",
        ]

        for field in author_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, list):
                    authors.extend(str(v) for v in value if v)
                elif isinstance(value, str):
                    authors.append(value.strip())
                elif isinstance(value, dict) and "text" in value:
                    authors.append(value["text"].strip())

        return authors if authors else None

    def _extract_publication_date(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract publication date from record data."""
        date_fields = [
            "originInfo/dateIssued",
            "dateIssued",
            "date",
            "Date",
            "publicationDate",
            "pubDate",
        ]

        for field in date_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict) and "text" in value:
                    return value["text"].strip()

        return None

    def _extract_publisher(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract publisher from record data."""
        publisher_fields = [
            "originInfo/publisher",
            "publisher",
            "Publisher",
        ]

        for field in publisher_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict) and "text" in value:
                    return value["text"].strip()

        return None

    def _extract_language(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract language from record data."""
        language_fields = [
            "language/languageTerm",
            "language",
            "Language",
        ]

        for field in language_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict) and "text" in value:
                    return value["text"].strip()

        return None

    def _extract_format_type(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract format type from record data."""
        format_fields = [
            "physicalDescription/form",
            "format",
            "Format",
            "resourceType",
            "type",
        ]

        for field in format_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict) and "text" in value:
                    return value["text"].strip()

        return None

    def _extract_subjects(self, data: Dict[str, Any], format_type: str) -> Optional[List[str]]:
        """Extract subjects from record data."""
        subjects = []

        subject_fields = [
            "subject/topic",
            "subject",
            "Subject",
        ]

        for field in subject_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, list):
                    subjects.extend(str(v) for v in value if v)
                elif isinstance(value, str):
                    subjects.append(value.strip())
                elif isinstance(value, dict) and "text" in value:
                    subjects.append(value["text"].strip())

        return subjects if subjects else None

    def _extract_description(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Extract description from record data."""
        desc_fields = [
            "abstract",
            "description",
            "Description",
            "note",
        ]

        for field in desc_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, str):
                    return value.strip()
                elif isinstance(value, dict) and "text" in value:
                    return value["text"].strip()

        return None

    def _extract_identifiers(self, data: Dict[str, Any], format_type: str) -> Dict[str, str]:
        """Extract identifiers from record data."""
        identifiers = {}

        # Common identifier types
        id_types = ["ISBN", "ISSN", "OCLC", "LCCN", "DOI"]

        for id_type in id_types:
            field_path = f"identifier[@type='{id_type.lower()}']"
            value = self._get_nested_value(data, field_path)
            if value:
                identifiers[id_type] = str(value)

        # Also check for generic identifier fields
        generic_fields = ["identifier", "id", "ID"]
        for field in generic_fields:
            value = data.get(field)
            if value and isinstance(value, str):
                # Try to detect type
                if value.startswith("978") or value.startswith("979"):
                    identifiers["ISBN"] = value
                elif value.startswith("977"):
                    identifiers["ISSN"] = value
                elif value.startswith("ocm"):
                    identifiers["OCLC"] = value
                else:
                    identifiers["ID"] = value

        return identifiers

    def _extract_holdings(self, data: Dict[str, Any], format_type: str) -> Optional[List[Dict[str, Any]]]:
        """Extract holdings information from record data."""
        holdings_fields = [
            "location",
            "holdings",
            "Holdings",
        ]

        for field in holdings_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, list):
                    return value
                elif isinstance(value, dict):
                    return [value]
                elif isinstance(value, str):
                    return [{"location": value}]

        return None

    def _extract_classification(self, data: Dict[str, Any], format_type: str) -> Optional[List[str]]:
        """Extract classification numbers from record data."""
        classifications = []

        class_fields = [
            "classification",
            "Classification",
            "lcc",
            "dewey",
        ]

        for field in class_fields:
            value = self._get_nested_value(data, field)
            if value:
                if isinstance(value, list):
                    classifications.extend(str(v) for v in value if v)
                elif isinstance(value, str):
                    classifications.append(value.strip())

        return classifications if classifications else None

    def _extract_collections(self, data: Dict[str, Any], format_type: str) -> Optional[List[str]]:
        """Extract collection information from record data."""
        collections = []

        collection_fields = [
            "setName",
            "collection",
            "Collection",
            "setSpec",
        ]

        for field in collection_fields:
            value = data.get(field)
            if value:
                if isinstance(value, list):
                    collections.extend(str(v) for v in value if v)
                elif isinstance(value, str):
                    collections.append(value.strip())

        return collections if collections else None

    def _extract_stackscore(self, data: Dict[str, Any], format_type: str) -> Optional[float]:
        """Extract stackscore from record data."""
        stackscore_fields = [
            "stackscore",
            "Stackscore",
            "usage",
            "popularity",
        ]

        for field in stackscore_fields:
            value = data.get(field)
            if value:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_digital_content(self, data: Dict[str, Any], format_type: str) -> bool:
        """Extract digital content availability from record data."""
        digital_fields = [
            "digital",
            "online",
            "electronic",
            "hasDigital",
        ]

        for field in digital_fields:
            value = data.get(field)
            if value:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ("true", "yes", "1")

        return False

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using path notation."""
        keys = path.split("/")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current