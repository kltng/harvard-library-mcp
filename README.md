# Harvard Library MCP Server

A Model Context Protocol (MCP) server for the Harvard University Library catalog API, providing comprehensive bibliographic search and metadata retrieval capabilities for AI assistants.

[![PyPI version](https://badge.fury.io/py/harvard-library-mcp.svg)](https://badge.fury.io/py/harvard-library-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/harvard-library-mcp.svg)](https://pypi.org/project/harvard-library-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🔍 Comprehensive Search**: Free-text search, advanced fielded search, collection-specific queries
- **📚 Rich Metadata**: Native MODS XML format with structured JSON conversion
- **🔌 Universal Integration**: stdio MCP transport for Claude Desktop, Cherry Studio, and other AI assistants
- **⚡ High Performance**: Async HTTP client with built-in rate limiting and error handling
- **🌐 Access to 20M+ Records**: Search Harvard's entire academic library collection
- **📖 Complete Metadata**: Access to bibliographic records, subject headings, and collection information

## 🚀 Quick Start

### Installation from PyPI

```bash
pip install harvard-library-mcp
```

### Usage with AI Assistants

#### Cherry Studio Integration

Cherry Studio provides native MCP server support for seamless integration with the Harvard Library catalog.

**Prerequisites:**
- Cherry Studio installed on your system
- `harvard-library-mcp` package installed via `pip install harvard-library-mcp`

**Step 1: Install MCP Environment**
1. Open Cherry Studio → Settings → MCP Server
2. Click "Install" to automatically install required dependencies
3. If installation fails, manually install to the Cherry Studio directory:
   - **Windows**: `C:\Users\{username}\.cherrystudio\bin`
   - **macOS/Linux**: `~/.cherrystudio/bin`

**Step 2: Configure Harvard Library MCP Server**
Cherry Studio may use the standard MCP configuration format. Add the following to your Cherry Studio MCP settings:

```json
{
  "mcp": {
    "servers": {
      "harvard-library": {
        "command": "uvx",
        "args": ["harvard-library-mcp"],
        "env": {}
      }
    }
  }
}
```

**Alternative Cherry Studio Format**
If Cherry Studio uses its own format, use this configuration:

```json
{
  "name": "Harvard Library",
  "command": "uvx",
  "args": ["harvard-library-mcp"],
  "description": "Search Harvard University Library catalog - 20M+ academic records",
  "tools": [
    "search_catalog",
    "search_by_title",
    "search_by_author",
    "search_by_subject",
    "advanced_search",
    "search_by_collection",
    "search_by_date_range",
    "search_by_geographic_origin",
    "get_record_details",
    "get_collections_list",
    "parse_mods_metadata"
  ],
  "icon": "📚",
  "category": "Research",
  "version": "0.1.0"
}
```

**Step 3: Start Using**
1. Restart Cherry Studio
2. The Harvard Library tools will be available in your chat interface
3. Try queries like:
   - "Search for books about machine learning"
   - "Find works by Shakespeare in Harvard's collection"
   - "Show me records from the Harvard Fine Arts Library"

#### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcp": {
    "servers": {
      "harvard-library": {
        "command": "uvx",
        "args": ["harvard-library-mcp"]
      }
    }
  }
}
```

**Configuration File Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### Standard MCP Configuration

For any MCP-compatible client, use this JSON configuration format:

```json
{
  "mcp": {
    "servers": {
      "harvard-library": {
        "command": "uvx",
        "args": ["harvard-library-mcp"],
        "env": {}
      }
    }
  }
}
```

**Configuration Options:**
- `command`: The command to run (`uvx` for running from PyPI packages)
- `args`: Package name and additional arguments (`["harvard-library-mcp"]`)
- `env`: Environment variables for the server process (optional)

**Example with custom settings:**
```json
{
  "mcp": {
    "servers": {
      "harvard-library": {
        "command": "uvx",
        "args": ["harvard-library-mcp"],
        "env": {
          "LOG_LEVEL": "DEBUG",
          "RATE_LIMIT_REQUESTS_PER_SECOND": "5"
        }
      }
    }
  }
}
```

**Note:** Using `uvx harvard-library-mcp` is the recommended approach as it automatically handles virtual environments and dependencies from PyPI.

#### Local Development

```bash
# Clone and install in development mode
git clone https://github.com/your-username/harvard-library-mcp.git
cd harvard-library-mcp
pip install -e .

# Run as MCP server (stdio)
python -m harvard_library_mcp.server
```

## 🛠️ Available MCP Tools

### 🔍 Search Tools
- **`search_catalog(query)`** - Free-text search across entire Harvard Library catalog
- **`search_by_title(title)`** - Search specifically by title field
- **`search_by_author(author)`** - Search by author/creator names
- **`search_by_subject(subject)`** - Search by subject headings and keywords
- **`advanced_search(filters)`** - Multi-field search with specific filters (title, author, subject, date, etc.)
- **`search_by_collection(collection_id)`** - Search within specific Harvard Library collections
- **`search_by_date_range(start_date, end_date)`** - Search by publication date range
- **`search_by_geographic_origin(location)`** - Search by publication location

### 📊 Utility Tools
- **`get_record_details(record_id)`** - Fetch complete bibliographic record by Harvard ID
- **`get_collections_list()`** - List all available collections with metadata
- **`parse_mods_metadata(mods_xml)`** - Convert MODS XML to structured JSON

## 📝 Usage Examples

### Basic Search
```
Search for books about artificial intelligence published after 2020
```

### Academic Research
```
Find works by Noam Chomsky in the linguistics collection
Show me details for Harvard record ID: 12345678
```

### Collection Discovery
```
List all Harvard Library collections
Search within the Fine Arts Library collection for Renaissance art
```

## ⚙️ Configuration

### Environment Variables
- `HARVARD_API_BASE_URL`: Base URL for Harvard Library API (default: `https://api.lib.harvard.edu/v2`)
- `RATE_LIMIT_REQUESTS_PER_SECOND`: API rate limit (default: `10`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Advanced Configuration
For custom deployments, you can configure additional settings:

```bash
# Custom rate limiting
export RATE_LIMIT_REQUESTS_PER_SECOND=5

# Debug logging
export LOG_LEVEL=DEBUG

# Custom API endpoint (for development/testing)
export HARVARD_API_BASE_URL=https://api.lib.harvard.edu/v2
```

## 🏗️ Architecture

### Core Components
- **Server (`server.py`)**: MCP stdio interface implementation
- **API Client (`api/client.py`)**: Async HTTP client for Harvard Library API
- **Tools (`tools/search_tools.py`)**: MCP tool implementations
- **Models (`models/harvard_models.py`)**: Pydantic models for data validation
- **Configuration (`config.py`)**: Environment-based configuration management

### Data Flow
```
AI Assistant → MCP Server → Harvard Library API → Bibliographic Records
```

The server handles:
- ✅ Rate limiting (10 req/sec default)
- ✅ Error handling and retries
- ✅ MODS XML parsing and JSON conversion
- ✅ Response validation and typing

## 👨‍💻 Development

### Prerequisites
- Python 3.11 or higher
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/harvard-library-mcp.git
cd harvard-library-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test
pytest tests/ -v

# Run tests with coverage
make test-coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/ -m unit        # Unit tests only
pytest tests/ -m integration # Integration tests only
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

## 🐳 Docker Support

### Build and Run

```bash
# Build Docker image
docker build -t harvard-library-mcp:latest .

# Run container
docker run -d --name harvard-library-mcp harvard-library-mcp:latest

# Using Docker Compose
docker-compose up -d
docker-compose logs -f
```

## 📦 Installation Options

### From PyPI (Recommended)
```bash
pip install harvard-library-mcp
```

### From Source
```bash
git clone https://github.com/your-username/harvard-library-mcp.git
cd harvard-library-mcp
pip install -e .
```

### Development Version
```bash
pip install git+https://github.com/your-username/harvard-library-mcp.git
```

## 🔄 Release Process

This project uses automated releases with GitHub Actions and PyPI Trusted Publishing.

### For Users

**Install the latest version:**
```bash
pip install harvard-library-mcp
```

**Install a specific version:**
```bash
pip install harvard-library-mcp==0.1.0
```

### For Maintainers

#### Automated Release Process
The project includes comprehensive GitHub Actions for:
- ✅ Multi-Python version testing (3.11, 3.12, 3.13)
- ✅ Code quality checks (ruff, black, isort, mypy)
- ✅ Security scanning (bandit, pip-audit)
- ✅ Package validation and PyPI publishing
- ✅ GitHub Release creation

#### Manual Release Steps
1. Update version numbers in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md` with release notes
3. Run `make test` to ensure all tests pass
4. Commit and push changes
5. Trigger "Release to PyPI" workflow from GitHub Actions

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links & Resources

- **PyPI Package**: https://pypi.org/project/harvard-library-mcp/
- **GitHub Repository**: https://github.com/your-username/harvard-library-mcp
- **Bug Reports**: https://github.com/your-username/harvard-library-mcp/issues
- **Harvard Library API Documentation**:
  - [LibraryCloud API](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43287734/LibraryCloud+APIs)
  - [LibraryCloud Overview](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43286729/LibraryCloud)
- **MODS XML Schema**: http://www.loc.gov/standards/mods/

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Project Statistics

- **Total Records**: 20M+ bibliographic records
- **Collections**: 100+ specialized library collections
- **API Rate Limit**: 10 requests/second (configurable)
- **Response Formats**: JSON, MODS XML
- **Python Versions**: 3.11, 3.12, 3.13
- **License**: MIT

---

**⭐ Star this repository on GitHub if you find it useful!**

Made with ❤️ for the academic research community