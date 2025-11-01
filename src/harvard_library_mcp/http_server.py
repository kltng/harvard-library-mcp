"""HTTP server interface for Harvard Library MCP server using FastAPI."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import __version__
from .config import settings
from .tools.search_tools import (
    advanced_search,
    get_collections_list,
    get_record_details,
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

# Pydantic models for request/response
class SearchRequest(BaseModel):
    """Base search request model."""
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Results offset for pagination")
    response_format: str = Field(default="json", pattern="^(json|xml)$", description="Response format")


class CatalogSearchRequest(SearchRequest):
    """Catalog search request model."""
    query: str = Field(..., description="General search query")


class FieldSearchRequest(SearchRequest):
    """Field-specific search request model."""
    field_value: str = Field(..., description="Search value for the field")


class DateRangeSearchRequest(SearchRequest):
    """Date range search request model."""
    start_date: str = Field(..., pattern="^\\d{4}-\\d{2}-\\d{2}$", description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., pattern="^\\d{4}-\\d{2}-\\d{2}$", description="End date (YYYY-MM-DD)")
    query: Optional[str] = Field(default=None, description="Additional search query")


class GeographicSearchRequest(SearchRequest):
    """Geographic search request model."""
    origin_place: str = Field(..., description="Geographic origin place")
    query: Optional[str] = Field(default=None, description="Additional search query")


class AdvancedSearchRequest(SearchRequest):
    """Advanced search request model."""
    query: Optional[str] = Field(default=None, description="General search query")
    title: Optional[str] = Field(default=None, description="Title filter")
    author: Optional[str] = Field(default=None, description="Author filter")
    subject: Optional[str] = Field(default=None, description="Subject filter")
    collection: Optional[str] = Field(default=None, description="Collection filter")
    origin_place: Optional[str] = Field(default=None, description="Origin place filter")
    publication_place: Optional[str] = Field(default=None, description="Publication place filter")
    language: Optional[str] = Field(default=None, description="Language filter")
    format_type: Optional[str] = Field(default=None, description="Format type filter")
    start_date: Optional[str] = Field(default=None, pattern="^\\d{4}-\\d{2}-\\d{2}$", description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, pattern="^\\d{4}-\\d{2}-\\d{2}$", description="End date (YYYY-MM-DD)")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class RecordDetailsRequest(BaseModel):
    """Record details request model."""
    record_id: str = Field(..., description="Record identifier")
    response_format: str = Field(default="json", pattern="^(json|xml)$", description="Response format")


class ModsParseRequest(BaseModel):
    """MODS parsing request model."""
    mods_xml: str = Field(..., description="MODS XML content")


# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info(f"Starting Harvard Library HTTP Server v{__version__}")
    yield
    logger.info("Shutting down Harvard Library HTTP Server")


# Create FastAPI app
app = FastAPI(
    title="Harvard Library MCP Server",
    description="HTTP API for Harvard University Library catalog search",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "harvard-library-mcp",
        "version": __version__
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "name": "Harvard Library MCP Server",
        "version": __version__,
        "description": "HTTP API for Harvard University Library catalog search",
        "docs": "/docs",
        "endpoints": {
            "search": "/search",
            "search_title": "/search/title",
            "search_author": "/search/author",
            "search_subject": "/search/subject",
            "search_collection": "/search/collection",
            "search_date_range": "/search/date-range",
            "search_geographic": "/search/geographic",
            "advanced_search": "/search/advanced",
            "record": "/record/{record_id}",
            "collections": "/collections",
            "parse_mods": "/parse/mods"
        }
    }


# Search endpoints
@app.post("/search")
async def search_endpoint(request: CatalogSearchRequest):
    """Search the Harvard Library catalog."""
    try:
        result = await search_catalog(
            query=request.query,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/title")
async def search_by_title_endpoint(request: FieldSearchRequest):
    """Search by title."""
    try:
        result = await search_by_title(
            title=request.field_value,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Title search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/author")
async def search_by_author_endpoint(request: FieldSearchRequest):
    """Search by author."""
    try:
        result = await search_by_author(
            author=request.field_value,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Author search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/subject")
async def search_by_subject_endpoint(request: FieldSearchRequest):
    """Search by subject."""
    try:
        result = await search_by_subject(
            subject=request.field_value,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Subject search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/collection")
async def search_by_collection_endpoint(request: FieldSearchRequest):
    """Search within a collection."""
    try:
        result = await search_by_collection(
            collection=request.field_value,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Collection search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/date-range")
async def search_by_date_range_endpoint(request: DateRangeSearchRequest):
    """Search by date range."""
    try:
        result = await search_by_date_range(
            start_date=request.start_date,
            end_date=request.end_date,
            query=request.query,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Date range search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/geographic")
async def search_by_geographic_endpoint(request: GeographicSearchRequest):
    """Search by geographic origin."""
    try:
        result = await search_by_geographic_origin(
            origin_place=request.origin_place,
            query=request.query,
            limit=request.limit,
            offset=request.offset,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Geographic search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/advanced")
async def advanced_search_endpoint(request: AdvancedSearchRequest):
    """Advanced search with multiple filters."""
    try:
        result = await advanced_search(
            query=request.query,
            title=request.title,
            author=request.author,
            subject=request.subject,
            collection=request.collection,
            origin_place=request.origin_place,
            publication_place=request.publication_place,
            language=request.language,
            format_type=request.format_type,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            response_format=request.response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Record details endpoint
@app.get("/record/{record_id}")
async def get_record_endpoint(record_id: str, response_format: str = Query(default="json", pattern="^(json|xml)$")):
    """Get record details by ID."""
    try:
        result = await get_record_details(
            record_id=record_id,
            response_format=response_format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Record details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Collections endpoint
@app.get("/collections")
async def get_collections_endpoint():
    """Get list of available collections."""
    try:
        result = await get_collections_list()
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Collections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# MODS parsing endpoint
@app.post("/parse/mods")
async def parse_mods_endpoint(request: ModsParseRequest):
    """Parse MODS XML metadata."""
    try:
        result = await parse_mods_metadata(mods_xml=request.mods_xml)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"MODS parsing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Simple GET endpoints for basic searches
@app.get("/search")
async def simple_search_endpoint(
    q: str = Query(..., description="Search query"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    format: str = Query(default="json", pattern="^(json|xml)$")
):
    """Simple search via GET parameters."""
    try:
        result = await search_catalog(
            query=q,
            limit=limit,
            offset=offset,
            response_format=format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Simple search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/author")
async def simple_author_search_endpoint(
    author: str = Query(..., description="Author search query"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    format: str = Query(default="json", pattern="^(json|xml)$")
):
    """Simple author search via GET parameters."""
    try:
        result = await search_by_author(
            author=author,
            limit=limit,
            offset=offset,
            response_format=format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Simple author search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/title")
async def simple_title_search_endpoint(
    title: str = Query(..., description="Title search query"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    format: str = Query(default="json", pattern="^(json|xml)$")
):
    """Simple title search via GET parameters."""
    try:
        result = await search_by_title(
            title=title,
            limit=limit,
            offset=offset,
            response_format=format
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Simple title search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start_http_server():
    """Start the HTTP server."""
    logger.info(f"Starting Harvard Library HTTP Server on {settings.host}:{settings.port}")
    logger.info(f"API Documentation available at http://{settings.host}:{settings.port}/docs")

    uvicorn.run(
        "harvard_library_mcp.http_server:app",
        host=settings.host,
        port=settings.port,
        workers=settings.http_workers,
        reload=settings.http_reload,
        log_level=settings.log_level.lower(),
    )


def main():
    """CLI entry point for HTTP server."""
    try:
        start_http_server()
    except KeyboardInterrupt:
        logger.info("HTTP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"HTTP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()