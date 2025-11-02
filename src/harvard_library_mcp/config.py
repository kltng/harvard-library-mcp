"""Configuration settings for Harvard Library MCP Server."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Harvard Library MCP server."""

    # Harvard Library API Configuration
    harvard_api_base_url: str = Field(
        default="https://api.lib.harvard.edu/v2",
        description="Base URL for Harvard Library API"
    )
    harvard_api_timeout: int = Field(
        default=30,
        description="Timeout for API requests in seconds"
    )
    harvard_api_user_agent: str = Field(
        default="Harvard-Library-MCP/0.1.0",
        description="User agent string for API requests"
    )

    # Rate Limiting
    rate_limit_requests_per_second: int = Field(
        default=10,
        description="Maximum API requests per second"
    )
    rate_limit_burst_size: int = Field(
        default=20,
        description="Maximum burst size for rate limiting"
    )

    # Server Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    # Cache Configuration
    enable_cache: bool = Field(
        default=True,
        description="Enable response caching"
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )

    # Development
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # Pydantic v2 style configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
