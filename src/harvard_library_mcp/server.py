"""Main MCP server for Harvard Library catalog search."""

import asyncio
import logging
import sys
from typing import Any, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions

from . import __version__
from .config import settings
from .tools.search_tools import (
    advanced_search,
    get_collections_list,
    get_record_details,
    parse_permalink,
    parse_mods_metadata,
    search_by_author,
    search_by_collection,
    search_by_date_range,
    search_by_geographic_origin,
    search_by_subject,
    search_by_title,
    search_catalog,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("harvard-library-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools."""
    return [
        types.Tool(
            name="search_catalog",
            description="Search the Harvard Library catalog with a general query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "General search query string"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_by_title",
            description="Search the Harvard Library catalog by title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="search_by_author",
            description="Search the Harvard Library catalog by author",
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["author"]
            }
        ),
        types.Tool(
            name="search_by_subject",
            description="Search the Harvard Library catalog by subject",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Subject search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["subject"]
            }
        ),
        types.Tool(
            name="search_by_collection",
            description="Search within a specific Harvard Library collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "Collection name or identifier (setName parameter)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["collection"]
            }
        ),
        types.Tool(
            name="search_by_date_range",
            description="Search the Harvard Library catalog by publication date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional additional search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        types.Tool(
            name="search_by_geographic_origin",
            description="Search the Harvard Library catalog by geographic origin",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin_place": {
                        "type": "string",
                        "description": "Geographic origin place for filtering"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional additional search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["origin_place"]
            }
        ),
        types.Tool(
            name="advanced_search",
            description="Perform advanced search with multiple filters on the Harvard Library catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "General search query"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title filter"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author filter"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Subject filter"
                    },
                    "collection": {
                        "type": "string",
                        "description": "Collection filter"
                    },
                    "origin_place": {
                        "type": "string",
                        "description": "Origin place filter"
                    },
                    "publication_place": {
                        "type": "string",
                        "description": "Publication place filter"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language filter"
                    },
                    "format_type": {
                        "type": "string",
                        "description": "Format type filter"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "minimum": 0,
                        "default": 0
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort field"
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Sort order",
                        "enum": ["asc", "desc"],
                        "default": "asc"
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                }
            }
        ),
        types.Tool(
            name="get_record_details",
            description="Get detailed information for a specific Harvard Library catalog record",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "string",
                        "description": "Unique identifier for the record"
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "xml"],
                        "default": "json"
                    }
                },
                "required": ["record_id"]
            }
        ),
        types.Tool(
            name="get_collections_list",
            description="Get a list of available Harvard Library collections",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="parse_mods_metadata",
            description="Parse MODS XML metadata and extract structured information",
            inputSchema={
                "type": "object",
                "properties": {
                    "mods_xml": {
                        "type": "string",
                        "description": "MODS XML content as string"
                    }
                },
                "required": ["mods_xml"]
            }
        ),
        types.Tool(
            name="parse_permalink",
            description="Compute Harvard catalog permalink (alma) from identifiers or MODS",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string", "description": "Record identifier (optional)"},
                    "identifiers": {"type": "object", "description": "Identifiers map (optional)"},
                    "mods_xml": {"type": "string", "description": "MODS XML (optional)"},
                    "mods_dict": {"type": "object", "description": "MODS dict (optional)"}
                }
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls."""
    try:
        if arguments is None:
            arguments = {}

        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        # Route to appropriate tool function
        if name == "search_catalog":
            result = await search_catalog(**arguments)
        elif name == "search_by_title":
            result = await search_by_title(**arguments)
        elif name == "search_by_author":
            result = await search_by_author(**arguments)
        elif name == "search_by_subject":
            result = await search_by_subject(**arguments)
        elif name == "search_by_collection":
            result = await search_by_collection(**arguments)
        elif name == "search_by_date_range":
            result = await search_by_date_range(**arguments)
        elif name == "search_by_geographic_origin":
            result = await search_by_geographic_origin(**arguments)
        elif name == "advanced_search":
            result = await advanced_search(**arguments)
        elif name == "get_record_details":
            result = await get_record_details(**arguments)
        elif name == "get_collections_list":
            result = await get_collections_list()
        elif name == "parse_mods_metadata":
            result = await parse_mods_metadata(**arguments)
        elif name == "parse_permalink":
            result = await parse_permalink(**arguments)
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}",
            }

        logger.info(f"Tool {name} completed successfully")
        return [types.TextContent(type="text", text=str(result))]

    except Exception as e:
        error_msg = f"Error calling tool {name}: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=str({"success": False, "error": error_msg}))]


# Resources removed - all functionality available through tools


async def main():
    """Main server entry point."""
    logger.info(f"Starting Harvard Library MCP Server v{__version__}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"API Base URL: {settings.harvard_api_base_url}")
    logger.info(f"Rate Limit: {settings.rate_limit_requests_per_second} req/s")

    # Create proper capabilities object
    from mcp.server.models import ServerCapabilities
    capabilities = ServerCapabilities(
        tools={},
        resources={},
        prompts=None,
        logging=None
    )

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="harvard-library-mcp",
                server_version=__version__,
                capabilities=capabilities,
            ),
        )


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
