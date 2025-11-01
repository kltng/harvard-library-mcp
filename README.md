# Harvard Library MCP Server

A Model Context Protocol (MCP) server for the Harvard University Library catalog API, providing both stdio and HTTP interfaces for comprehensive bibliographic search and metadata retrieval.

## Features

- **Comprehensive Search**: Basic keyword search, advanced fielded search, collection-specific search
- **Rich Metadata**: Native MODS XML format support with structured JSON conversion
- **Dual Interface**: Both stdio transport for local use and HTTP streaming for remote access
- **Python Implementation**: Robust async HTTP client with proper error handling
- **Docker Ready**: Containerized deployment with health checks
- **Rate Limited**: Respectful API usage with built-in rate limiting

## Quick Start

### Local Development

```bash
# Clone and install
git clone <repository-url>
cd harvard-library-mcp
pip install -e .

# Run as MCP server (stdio)
python -m harvard_library_mcp.server

# Run HTTP server
python -m harvard_library_mcp.http_server
```

### Docker Deployment

```bash
# Build and run
docker build -t harvard-library-mcp .
docker run -p 8000:8000 harvard-library-mcp

# Or with docker-compose
docker-compose up
```

## API Endpoints

The MCP server provides the following tools:

### Search Tools
- `search_catalog` - Free-text search across catalog
- `search_by_title` - Search by title
- `search_by_author` - Search by author
- `search_by_subject` - Search by subject/keywords
- `advanced_search` - Multi-field search with filters
- `search_by_collection` - Search within specific collections
- `search_by_date_range` - Search by publication date range
- `search_by_geographic_origin` - Search by publication location

### Utility Tools
- `get_record_details` - Fetch complete record by ID
- `get_collections_list` - List available collections
- `parse_mods_metadata` - Extract structured data from MODS

## Configuration

Environment variables:
- `HARVARD_API_BASE_URL`: Base URL for Harvard Library API (default: https://api.lib.harvard.edu/v2)
- `RATE_LIMIT_REQUESTS_PER_SECOND`: API rate limit (default: 10)
- `LOG_LEVEL`: Logging level (default: INFO)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
isort src/
```

## License

MIT License - see LICENSE file for details.

## Harvard Library API Documentation

- [LibraryCloud API Documentation](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43287734/LibraryCloud+APIs)
- [LibraryCloud Overview](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43286729/LibraryCloud)