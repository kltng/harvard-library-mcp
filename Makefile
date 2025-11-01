# Harvard Library MCP Server Makefile

.PHONY: help install install-dev test test-coverage lint format clean build run-mcp

# Default target
help:
	@echo "Harvard Library MCP Server - Available commands:"
	@echo ""
	@echo "  install        Install package dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  run-mcp       Start MCP server (stdio)"
	
# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code quality
lint:
	@echo "Running linting checks..."
	mypy src/
	ruff check src/
	black --check src/
	isort --check-only src/

format:
	@echo "Formatting code..."
	black src/
	isort src/
	ruff check --fix src/

# Cleaning
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	@echo "Building package..."
	python -m build


# Development helpers
dev-setup: install-dev
	@echo "Setting up development environment..."
	pre-commit install

run-mcp:
	@echo "Starting MCP server..."
	python -m harvard_library_mcp.server


# Database/Cache (for future enhancements)
redis-up:
	@echo "Starting Redis for caching..."
	docker run -d --name harvard-mcp-redis -p 6379:6379 redis:7-alpine

redis-down:
	@echo "Stopping Redis..."
	docker stop harvard-mcp-redis || true
	docker rm harvard-mcp-redis || true