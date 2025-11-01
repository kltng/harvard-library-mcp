# Harvard Library MCP Server - Deployment Guide

## Overview

The Harvard Library MCP Server can be deployed in multiple ways:
- As an MCP server using stdio transport (for Claude Desktop and other MCP clients)
- As an HTTP server with REST API endpoints
- Using Docker containers for production deployment

## Prerequisites

- Python 3.11 or higher
- Network access to Harvard Library API (internet connectivity)
- For Docker deployment: Docker and Docker Compose

## Installation

### From Source

```bash
git clone <repository-url>
cd harvard-library-mcp
pip install -e .
```

### From PyPI (when published)

```bash
pip install harvard-library-mcp
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `HARVARD_API_BASE_URL` | `https://api.lib.harvard.edu/v2` | Harvard Library API base URL |
| `RATE_LIMIT_REQUESTS_PER_SECOND` | `10` | API rate limiting |
| `HOST` | `0.0.0.0` | HTTP server bind address |
| `PORT` | `8000` | HTTP server port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Deployment Methods

### 1. MCP Server (stdio transport)

For use with Claude Desktop and other MCP clients:

```bash
# Direct execution
python -m harvard_library_mcp.server

# Or using the installed command
harvard-library-mcp
```

#### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "harvard-library": {
      "command": "harvard-library-mcp",
      "args": []
    }
  }
}
```

### 2. HTTP Server

For use as a REST API service:

```bash
# Direct execution
python -m harvard_library_mcp.http_server

# Or using the installed command
harvard-library-mcp-http
```

The HTTP server will start on `http://localhost:8000` by default.

#### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 3. Docker Deployment

#### Build Docker Image

```bash
docker build -t harvard-library-mcp:latest .
```

#### Run with Docker

```bash
# Basic run
docker run -d \
  --name harvard-library-mcp \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  harvard-library-mcp:latest
```

#### Run with Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 4. Production Deployment

#### Using Docker Compose (Recommended)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  harvard-library-mcp:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - RATE_LIMIT_REQUESTS_PER_SECOND=5
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Reverse proxy with nginx
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - harvard-library-mcp
```

#### Systemd Service

Create `/etc/systemd/system/harvard-library-mcp.service`:

```ini
[Unit]
Description=Harvard Library MCP Server
After=network.target

[Service]
Type=simple
User=mcpuser
WorkingDirectory=/opt/harvard-library-mcp
Environment=PATH=/opt/harvard-library-mcp/venv/bin
ExecStart=/opt/harvard-library-mcp/venv/bin/python -m harvard_library_mcp.http_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable harvard-library-mcp
sudo systemctl start harvard-library-mcp
```

## Scaling Considerations

### Load Balancing

For high-traffic deployments, consider using a load balancer:

```nginx
# nginx.conf
upstream harvard_mcp {
    server harvard-mcp-1:8000;
    server harvard-mcp-2:8000;
    server harvard-mcp-3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://harvard_mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Rate Limiting

Configure appropriate rate limits based on your usage:

```bash
# For development
RATE_LIMIT_REQUESTS_PER_SECOND=20

# For production
RATE_LIMIT_REQUESTS_PER_SECOND=5
```

### Caching

For future enhancement, consider adding Redis caching:

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  harvard-library-mcp:
    environment:
      - REDIS_URL=redis://redis:6379
      - ENABLE_CACHE=true
      - CACHE_TTL_SECONDS=300
```

## Monitoring

### Health Checks

The server provides a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "harvard-library-mcp",
  "version": "0.1.0"
}
```

### Logging

Configure logging levels and output:

```bash
# Development - verbose logging
LOG_LEVEL=DEBUG

# Production - error logging only
LOG_LEVEL=ERROR
```

Log files are written to `/app/logs` when running in Docker.

### Metrics (Future Enhancement)

Consider adding Prometheus metrics for monitoring:
- Request count and duration
- API response status codes
- Rate limiting statistics
- Error rates

## Security Considerations

1. **Network Security**: Run behind firewall/reverse proxy
2. **Input Validation**: All inputs are validated by Pydantic models
3. **Rate Limiting**: Built-in rate limiting prevents API abuse
4. **Authentication**: Currently uses public API (no auth required)
5. **HTTPS**: Use HTTPS in production (nginx reverse proxy recommended)

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check internet connectivity
   - Verify API base URL
   - Check firewall settings

2. **Rate Limiting**
   - Reduce `RATE_LIMIT_REQUESTS_PER_SECOND`
   - Check for concurrent requests

3. **Memory Issues**
   - Reduce `limit` parameter in search requests
   - Monitor memory usage

4. **Docker Issues**
   - Check Docker logs: `docker-compose logs`
   - Verify port availability
   - Check resource limits

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python -m harvard_library_mcp.http_server
```

## Support

For issues and questions:
- Check the GitHub repository issues
- Review the API documentation
- Check the Harvard Library API documentation

## API Limits

The Harvard Library API is public and doesn't require authentication, but has implicit rate limits:
- Recommended: ≤10 requests per second
- Burst: ≤20 requests
- Respect `429 Too Many Requests` responses

Always implement proper error handling and retry logic in your applications.