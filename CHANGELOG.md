# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Automated PyPI release workflow
- Enhanced testing and CI/CD pipeline
- Improved documentation and examples

## [0.1.0] - 2025-01-01

### Added
- Initial release of Harvard Library MCP server
- MCP server with stdio transport integration
- HTTP server with FastAPI and REST endpoints
- Comprehensive search tools for Harvard Library catalog:
  - Free-text catalog search
  - Title, author, and subject-specific searches
  - Advanced multi-field search with filters
  - Collection-based searching
  - Date range and geographic origin searches
- Utility tools for:
  - Record detail retrieval
  - Collections listing
  - MODS XML metadata parsing
- Harvard Library API integration with rate limiting
- Pydantic models for data validation
- Comprehensive test suite with pytest
- Development environment with code quality tools
- Docker support for containerized deployment
- MIT license

### Features
- **Search Capabilities**: Access to Harvard University Library's comprehensive catalog
- **Multiple Interfaces**: Both MCP (stdio) and HTTP server modes
- **Rate Limiting**: Configurable rate limiting for API calls
- **Error Handling**: Comprehensive error handling with retry logic
- **Metadata Support**: Native MODS XML format preservation with JSON conversion
- **Testing**: Unit and integration tests with mocking
- **Code Quality**: Linting, formatting, and type checking
- **Documentation**: Comprehensive README and development guide

### Supported Python Versions
- Python 3.11+
- Tested on 3.11, 3.12, and 3.13

### Dependencies
- MCP Python SDK
- httpx for async HTTP client
- Pydantic for data validation
- FastAPI for HTTP API
- lxml for XML processing
- xmltodict for XML to JSON conversion

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Types

- **Stable releases**: X.Y.Z (e.g., 1.0.0)
- **Release candidates**: X.Y.ZrcN (e.g., 1.0.0rc1)
- **Alpha releases**: X.Y.ZaN (e.g., 1.0.0a1)
- **Beta releases**: X.Y.ZbN (e.g., 1.0.0b1)

## Release Process

### Automated Releases

This project uses automated releases via GitHub Actions:

1. **Version Update**: Update version in `pyproject.toml` and `src/harvard_library_mcp/__init__.py`
2. **Manual Trigger**: Run "Release to PyPI" workflow from GitHub Actions
3. **Automated Testing**: Comprehensive testing across Python versions and platforms
4. **Quality Checks**: Code quality, security scanning, and type checking
5. **Package Building**: Build source and wheel distributions
6. **PyPI Publishing**: Automatic publishing to PyPI using Trusted Publishing
7. **GitHub Release**: Automatic GitHub Release creation with changelog

### Quality Gates

Before each release, the automated pipeline ensures:

- ✅ All tests pass on Python 3.11, 3.12, and 3.13
- ✅ Code quality checks (ruff, black, isort) pass
- ✅ Type checking (mypy) passes
- ✅ Security scans pass
- ✅ Package installation works correctly
- ✅ Version consistency across files
- ✅ Semantic versioning format compliance

### Manual Testing

Before triggering a release, manually verify:

1. **Local Testing**: `make test` passes
2. **Integration Tests**: API calls work correctly
3. **Package Build**: `python -m build` succeeds
4. **Installation Test**: Install from wheel and test CLI commands
5. **Documentation**: README and examples are up to date

---

## Support

- **Issues**: [GitHub Issues](https://github.com/kltang/harvard-library-mcp/issues)
- **Documentation**: [README.md](https://github.com/kltang/harvard-library-mcp/blob/main/README.md)
- **PyPI**: [harvard-library-mcp on PyPI](https://pypi.org/project/harvard-library-mcp/)