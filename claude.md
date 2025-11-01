# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **harvard-library-mcp**, a Model Context Protocol (MCP) server that provides access to Harvard University Library's catalog API through stdio interface. It enables AI assistants to search comprehensive bibliographic records, retrieve metadata in native MODS XML format, and access collection-specific information from one of the world's largest academic library collections.

## Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Set up development environment (includes pre-commit hooks)
make dev-setup

# Install from PyPI (when published)
pip install harvard-library-mcp
```

### Running the Server
```bash
# Run MCP server (stdio mode, for Claude Desktop integration)
python -m harvard_library_mcp.server
harvard-library-mcp  # Using installed command

# Using Make shortcut
make run-mcp      # Start MCP server
```

### Testing
```bash
# Run all tests
make test
pytest tests/ -v

# Run tests with coverage
make test-coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest tests/ -m unit        # Unit tests only
pytest tests/ -m integration # Integration tests only
pytest tests/ -m "not slow"  # Skip slow tests
```

### Code Quality
```bash
# Run all linting checks
make lint
mypy src/
ruff check src/
black --check src/
isort --check-only src/

# Format code automatically
make format
black src/
isort src/
ruff check --fix src/
```

### Docker Operations
```bash
# Build Docker image
make docker-build
docker build -t harvard-library-mcp:latest .

# Run Docker container
make docker-run
docker run -d --name harvard-library-mcp -p 8000:8000 harvard-library-mcp:latest

# Using Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down

# Stop and clean up containers
make docker-stop
```

## Architecture

### Core Components

- **`src/harvard_library_mcp/server.py`** - Main MCP server implementation using stdio transport
- **`src/harvard_library_mcp/http_server.py`** - FastAPI-based HTTP server with REST endpoints
- **`src/harvard_library_mcp/api/client.py`** - HTTP client for Harvard Library API integration
- **`src/harvard_library_mcp/tools/search_tools.py`** - MCP tool implementations for catalog search
- **`src/harvard_library_mcp/models/harvard_models.py`** - Pydantic models for API response validation
- **`src/harvard_library_mcp/config.py`** - Configuration management with environment variables

### MCP Tools Available

#### Search Tools
1. **`search_catalog(query)`** - Free-text search across entire catalog
2. **`search_by_title(title)`** - Search specifically by title field
3. **`search_by_author(author)`** - Search by author/creator names
4. **`search_by_subject(subject)`** - Search by subject headings/keywords
5. **`advanced_search(filters)`** - Multi-field search with specific filters
6. **`search_by_collection(collection_id)`** - Search within specific collections
7. **`search_by_date_range(start_date, end_date)`** - Search by publication date range
8. **`search_by_geographic_origin(location)`** - Search by publication location

#### Utility Tools
9. **`get_record_details(record_id)`** - Fetch complete record by Harvard ID
10. **`get_collections_list()`** - List available collections with metadata
11. **`parse_mods_metadata(mods_xml)`** - Convert MODS XML to structured JSON

### API Integration

The server integrates with Harvard Library API:
- **Base URL**: `https://api.lib.harvard.edu/v2`
- **Search Endpoint**: `/search.json`
- **Record Endpoint**: `/items/{id}.json`
- **MODS Data**: Native XML format preservation with JSON conversion

Key features:
- **Rate Limiting**: Configurable rate limiting (default: 10 requests/second)
- **Response Parsing**: Handles both JSON and XML MODS formats
- **Error Handling**: Comprehensive error handling with retry logic
- **Metadata Preservation**: Maintains original MODS XML while providing JSON convenience

### Operation Modes

1. **stdio mode** - For direct MCP client integration (Claude Desktop, AI assistants)
2. **HTTP/SSE mode** - For web service integration with REST API endpoints

## Development Guidelines

### Code Organization

- Use MCP decorators (`@mcp.tool()`) for exposing functionality
- Implement async/await patterns for all I/O operations
- Use Pydantic models for request/response validation
- Follow FastAPI patterns for HTTP endpoint design
- Implement comprehensive error handling with proper HTTP status codes

### Configuration Management

Environment variables in `src/harvard_library_mcp/config.py`:
```python
HARVARD_API_BASE_URL="https://api.lib.harvard.edu/v2"
RATE_LIMIT_REQUESTS_PER_SECOND=10
HOST="0.0.0.0"
PORT=8000
LOG_LEVEL="INFO"
```

### Testing Approach

- **Unit Tests**: Mock external API calls using `respx`
- **Integration Tests**: Test against actual API (marked as `integration`)
- **Async Testing**: Use `pytest-asyncio` for async function testing
- **Coverage**: Maintain high test coverage with html reports
- **Markers**: Use pytest markers for test categorization

### API Response Handling

The codebase handles multiple response formats:
- **JSON Search Results**: Parsed into Pydantic models
- **MODS XML**: Preserved natively and converted to structured JSON
- **Error Responses**: Standardized error format with proper logging
- **Rate Limiting**: Automatic retry with exponential backoff

## Dependencies

Core dependencies managed in `pyproject.toml`:
- `mcp>=1.0.0` - MCP Python SDK
- `httpx>=0.27.0` - Async HTTP client for API calls
- `pydantic>=2.8.0` - Data validation and serialization
- `xmltodict>=0.13.0` - XML to JSON conversion
- `fastapi>=0.112.0` - HTTP API framework
- `uvicorn[standard]>=0.30.0` - ASGI server
- `lxml>=5.2.0` - XML processing

Development dependencies:
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async testing support
- `black>=24.0.0` - Code formatting
- `isort>=5.13.0` - Import sorting
- `mypy>=1.10.0` - Static type checking
- `ruff>=0.5.0` - Fast Python linter

## Project Structure

```
src/harvard_library_mcp/
├── __init__.py           # Package initialization
├── server.py            # MCP server (stdio transport)
├── http_server.py       # HTTP/FastAPI server
├── config.py            # Configuration management
├── api/
│   ├── __init__.py
│   └── client.py        # Harvard API client
├── tools/
│   ├── __init__.py
│   └── search_tools.py  # MCP tool implementations
├── models/
│   ├── __init__.py
│   └── harvard_models.py # Pydantic models
└── utils/
    ├── __init__.py
    └── helpers.py       # Utility functions

tests/                   # pytest test suite
docs/                    # Documentation
docker/                  # Docker configuration
```

## API Rate Limiting and Best Practices

### Harvard Library API Guidelines
- **Recommended Rate**: ≤10 requests per second
- **Burst Capacity**: ≤20 requests
- **Error Handling**: Respect `429 Too Many Requests` responses
- **Data Usage**: Use results responsibly and cache when appropriate

### Implementation Features
- **Automatic Rate Limiting**: Built-in rate limiting enforcement
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Handling**: 10-second default timeout for API calls
- **Error Recovery**: Graceful degradation on API failures

## Deployment

### Development
```bash
# Local development with hot reload
uvicorn harvard_library_mcp.http_server:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Using Docker Compose (recommended)
docker-compose -f docker-compose.prod.yml up -d

# Using systemd service
sudo systemctl enable harvard-library-mcp
sudo systemctl start harvard-library-mcp
```

### Environment Configuration
Create `.env` file from `.env.example`:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Monitoring and Troubleshooting

### Health Checks
- **HTTP Endpoint**: `GET /health`
- **MCP Tools**: All tools return structured error responses
- **Logging**: Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### Common Issues
1. **API Connectivity**: Check internet connection and firewall settings
2. **Rate Limiting**: Reduce request rate or implement caching
3. **Memory Usage**: Limit search result sizes for large queries
4. **XML Parsing**: Handle malformed MODS XML gracefully

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python -m harvard_library_mcp.http_server
```

## Harvard Library API Documentation

- [LibraryCloud API Documentation](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43287734/LibraryCloud+APIs)
- [LibraryCloud Overview](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43286729/LibraryCloud)
- [MODS XML Schema](http://www.loc.gov/standards/mods/)

## Contributing Guidelines

### Code Style
- Follow PEP 8 with Black formatting (88 character line length)
- Use isort for import organization
- Type hints required for all functions (mypy compliance)
- Document all public functions and classes

### Testing Requirements
- Write tests for all new functionality
- Maintain >90% test coverage
- Use descriptive test names
- Mock external dependencies in unit tests

### Git Workflow
- Feature branches from main/master
- Descriptive commit messages
- Pull requests with code review
- Automated CI/CD pipeline checks