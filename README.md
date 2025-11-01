# Harvard Library MCP Server

A Model Context Protocol (MCP) server for the Harvard University Library catalog API, providing stdio interface for comprehensive bibliographic search and metadata retrieval.

## Features

- **Comprehensive Search**: Basic keyword search, advanced fielded search, collection-specific search
- **Rich Metadata**: Native MODS XML format support with structured JSON conversion
- **Stdio Interface**: MCP stdio transport for AI assistant integration
- **Python Implementation**: Robust async HTTP client with proper error handling
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
```

## MCP Tools

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

## Release Process

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

#### Prerequisites
1. PyPI Trusted Publishing must be configured (see `scripts/setup-pypi-trusted-publishing.md`)
2. You must be a project owner on PyPI
3. Repository permissions must allow workflow dispatch

#### Release Steps

1. **Update Version Numbers**
   ```bash
   # Update version in both files consistently
   # pyproject.toml
   # src/harvard_library_mcp/__init__.py
   ```

2. **Update Changelog**
   ```bash
   # Add release notes to CHANGELOG.md
   # Include new features, bug fixes, and breaking changes
   ```

3. **Test Locally**
   ```bash
   # Run full test suite
   make test

   # Build package to verify
   python -m build

   # Test installation
   pip install dist/*.whl
   harvard-library-mcp --help
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Release v0.1.0"
   git push
   ```

5. **Trigger Release Workflow**
   - Go to Actions → Release to PyPI
   - Click "Run workflow"
   - Set version (e.g., `0.1.0`)
   - Set dry_run to `false` for production release
   - Enable GitHub Release creation

6. **Monitor Release**
   - Watch workflow progress for any issues
   - Verify PyPI publishing completes
   - Check GitHub Release creation
   - Test installation from PyPI

#### Dry Run Testing

To test the release process without publishing:
```bash
# Trigger workflow with:
version: "0.1.0-test"
dry_run: true
create_github_release: false
```

#### Quality Gates

The automated release process ensures:
- ✅ All tests pass on Python 3.11, 3.12, 3.13
- ✅ Code quality checks (ruff, black, isort)
- ✅ Type checking (mypy)
- ✅ Security scanning (bandit, pip-audit)
- ✅ Package validation (twine check)
- ✅ Version consistency across files
- ✅ Semantic versioning compliance

#### Rollback Process

If a release has issues:
1. **Yank PyPI Version** (if dangerous):
   - Go to PyPI project page
   - Find the problematic version
   - Click "Yank" (keeps downloads but marks as deprecated)

2. **Fix Issues**:
   - Fix bugs in a new commit
   - Increment version appropriately
   - Release new version

3. **Communicate**:
   - Update GitHub Release with notes
   - Add entry to CHANGELOG.md
   - Notify users if breaking changes

### Release History

See [CHANGELOG.md](./CHANGELOG.md) for detailed release notes.

## License

MIT License - see LICENSE file for details.

## Harvard Library API Documentation

- [LibraryCloud API Documentation](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43287734/LibraryCloud+APIs)
- [LibraryCloud Overview](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43286729/LibraryCloud)