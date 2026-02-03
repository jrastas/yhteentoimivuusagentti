# Dockerfile for Yhteentoimivuusalusta MCP Server
# Provides sandboxed execution with minimal attack surface

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir hatchling

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Build wheel
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels .

# --- Production stage ---
FROM python:3.11-slim

# Security: Create non-root user with home directory
RUN groupadd -r mcp && useradd -r -g mcp -m -d /home/mcpuser mcpuser

WORKDIR /app

# Install the wheel and dependencies
COPY --from=builder /app/wheels/*.whl /app/wheels/
RUN pip install --no-cache-dir /app/wheels/*.whl && \
    pip install --no-cache-dir rapidfuzz>=3.6.0 && \
    rm -rf /app/wheels

# Create cache directory with proper permissions
RUN mkdir -p /app/cache && chown -R mcpuser:mcp /app/cache

# Create config.yaml that uses /app/cache for caching
RUN printf 'cache:\n  enabled: true\n  directory: /app/cache\n' > /app/config.yaml && \
    chown mcpuser:mcp /app/config.yaml

# Switch to non-root user
USER mcpuser

# Set working directory to /app so config.yaml is found
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV YHTEENTOIMIVUUSALUSTA_CACHE_DIR=/app/cache

# Health check - verify the module can be imported
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import yhteentoimivuusalusta_mcp.server" || exit 1

# Run the MCP server via stdio
CMD ["python", "-m", "yhteentoimivuusalusta_mcp.server"]
