"""Helper utility functions for data processing."""

import re
from typing import Dict, List, Optional, Union


def clean_text(text: Union[str, Dict, List]) -> Optional[str]:
    """
    Clean and normalize text from various input formats.

    Args:
        text: Text that might be a string, dict with 'text' key, or list

    Returns:
        Cleaned string or None if input is empty/invalid
    """
    if text is None:
        return None

    if isinstance(text, str):
        return text.strip() if text.strip() else None

    if isinstance(text, dict):
        if 'text' in text:
            return str(text['text']).strip() if str(text['text']).strip() else None
        # If it's a simple dict without 'text', try to get first value
        values = list(text.values())
        return str(values[0]).strip() if values else None

    if isinstance(text, list):
        # Join list items with space or return first meaningful item
        for item in text:
            if item and str(item).strip():
                return str(item).strip()
        return None

    return str(text).strip() if str(text).strip() else None


def format_author_name(author: Union[str, Dict, List]) -> Optional[str]:
    """
    Format author name from various input formats.

    Args:
        author: Author information that might be a string, dict, or list

    Returns:
        Formatted author name or None
    """
    if author is None:
        return None

    if isinstance(author, str):
        # Clean up the author name
        return re.sub(r'\s+', ' ', author.strip())

    if isinstance(author, dict):
        # Handle different possible keys for author name
        name_parts = []
        for key in ['namePart', 'name', 'displayForm', 'full']:
            if key in author:
                name_parts.append(clean_text(author[key]))

        # Try to construct name from parts
        if name_parts:
            return ' '.join(filter(None, name_parts))

        # Look for first/last name structure
        first_name = clean_text(author.get('firstName'))
        last_name = clean_text(author.get('lastName'))
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif last_name:
            return last_name
        elif first_name:
            return first_name

        # Fallback to any text content
        return clean_text(author)

    if isinstance(author, list):
        # Return the first valid author from the list
        for author_item in author:
            formatted = format_author_name(author_item)
            if formatted:
                return formatted

    return None


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize date string to consistent format.

    Args:
        date_str: Date string in various formats

    Returns:
        Normalized date string or None
    """
    if not date_str:
        return None

    # Remove extra whitespace
    date_str = str(date_str).strip()

    # Handle common date formats
    # Year only
    if re.match(r'^\d{4}$', date_str):
        return date_str

    # Year-month
    if re.match(r'^\d{4}-\d{1,2}$', date_str):
        parts = date_str.split('-')
        if len(parts) == 2:
            return f"{parts[0]}-{parts[1].zfill(2)}"

    # Full YYYY-MM-DD
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"

    # Handle year ranges like "2020-2022"
    if re.match(r'^\d{4}-\d{4}$', date_str):
        return date_str

    # Handle formats like "c. 2020" or "ca. 2020"
    if re.match(r'^[cC][aA]?\.?\s*\d{4}', date_str):
        year = re.search(r'\d{4}', date_str)
        return f"[{year.group()}]"

    # Handle date ranges with other characters
    if re.match(r'^\d{4}\s*[-/]\s*\d{4}', date_str):
        return re.sub(r'\s*[-/]\s*', '-', date_str)

    # Return original if can't normalize
    return date_str


def extract_isbn(identifiers: Dict[str, str]) -> Optional[str]:
    """
    Extract ISBN from identifiers dictionary.

    Args:
        identifiers: Dictionary containing various identifier types

    Returns:
        First ISBN found or None
    """
    if not identifiers:
        return None

    # Look for common ISBN keys
    isbn_keys = ['ISBN', 'isbn', 'isbn13', 'isbn10', 'ISBN-13', 'ISBN-10']

    for key in isbn_keys:
        if key in identifiers:
            isbn = str(identifiers[key]).strip()
            # Clean up ISBN (remove hyphens and spaces)
            isbn = re.sub(r'[-\s]', '', isbn)
            if isbn and len(isbn) in [10, 13]:
                return isbn

    return None


def format_identifiers(identifiers: Dict[str, str]) -> Dict[str, str]:
    """
    Format and normalize identifiers dictionary.

    Args:
        identifiers: Raw identifiers dictionary

    Returns:
        Formatted identifiers dictionary
    """
    if not identifiers:
        return {}

    formatted = {}
    identifier_mappings = {
        'isbn': 'ISBN',
        'issn': 'ISSN',
        'lccn': 'LCCN',
        'oclc': 'OCLC',
        'doi': 'DOI',
        'pmid': 'PMID',
    }

    for key, value in identifiers.items():
        if value and str(value).strip():
            # Normalize the key
            normalized_key = key.lower()
            mapped_key = identifier_mappings.get(normalized_key, key.upper())

            # Clean up the identifier value
            clean_value = str(value).strip()

            # Additional cleaning for specific identifier types
            if mapped_key in ['ISBN', 'ISSN']:
                clean_value = re.sub(r'[-\s]', '', clean_value)
            elif mapped_key == 'DOI':
                # Ensure DOI has proper format
                if not clean_value.startswith('10.'):
                    clean_value = f"10.{clean_value}"

            formatted[mapped_key] = clean_value

    return formatted


def extract_list_from_field(field: Union[str, List, Dict]) -> List[str]:
    """
    Extract a list of strings from various field formats.

    Args:
        field: Field that might be a string, list, or dict

    Returns:
        List of strings
    """
    if field is None:
        return []

    if isinstance(field, str):
        # Split by common separators
        items = re.split(r'[,;]\s*', field)
        return [item.strip() for item in items if item.strip()]

    if isinstance(field, list):
        result = []
        for item in field:
            if isinstance(item, str):
                result.append(item.strip())
            else:
                cleaned = clean_text(item)
                if cleaned:
                    result.append(cleaned)
        return result

    if isinstance(field, dict):
        # Try to find lists within dict
        for key in ['topics', 'subjects', 'terms']:
            if key in field:
                return extract_list_from_field(field[key])

        # Otherwise return text content as single item
        cleaned = clean_text(field)
        return [cleaned] if cleaned else []

    return []


def safe_int(value: Union[str, int, None], default: int = 0) -> int:
    """
    Safely convert value to integer with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value
    """
    if value is None:
        return default

    try:
        if isinstance(value, int):
            return value
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default


def safe_float(value: Union[str, float, None], default: float = 0.0) -> float:
    """
    Safely convert value to float with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value
    """
    if value is None:
        return default

    try:
        if isinstance(value, float):
            return value
        return float(str(value).strip())
    except (ValueError, TypeError):
        return default


def truncate_text(text: Optional[str], max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text:
        return ""

    text = str(text).strip()
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix