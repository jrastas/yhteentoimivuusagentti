# Docker Setup for Yhteentoimivuusalusta MCP Server

This guide explains how to run the MCP server in a Docker container for sandboxed, secure execution.

## Why Docker?

Running the MCP server in Docker provides:

- **Isolation**: The server cannot access your filesystem outside the container
- **Network control**: Limit which hosts the server can connect to
- **Resource limits**: Cap CPU and memory usage
- **Reproducibility**: Same environment everywhere
- **No system dependencies**: Python version and libraries are bundled

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Windows, macOS, or Linux

## Quick Start

### 1. Build the Docker Image

Open a terminal in the project directory and run:

```bash
docker build -t yhteentoimivuusalusta-mcp:latest .
```

Or using Docker Compose:

```bash
docker compose build
```

### 2. Test the Container

Verify the container starts correctly:

```bash
docker run --rm yhteentoimivuusalusta-mcp:latest python -c "import yhteentoimivuusalusta_mcp.server; print('OK')"
```

### 3. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "yhteentoimivuusalusta-cache:/app/cache",
        "yhteentoimivuusalusta-mcp:latest"
      ]
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server should now appear in the available tools.

## Configuration Options

### Persistent Cache

The default configuration uses a Docker volume for caching. To use a local directory instead:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "C:/path/to/cache:/app/cache",
        "yhteentoimivuusalusta-mcp:latest"
      ]
    }
  }
}
```

### Custom Configuration File

Mount a custom `config.yaml`:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "yhteentoimivuusalusta-cache:/app/cache",
        "-v", "C:/path/to/config.yaml:/app/config.yaml:ro",
        "yhteentoimivuusalusta-mcp:latest"
      ]
    }
  }
}
```

### Resource Limits

Add resource constraints for additional security:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--memory=512m",
        "--cpus=1.0",
        "--read-only",
        "-v", "yhteentoimivuusalusta-cache:/app/cache",
        "yhteentoimivuusalusta-mcp:latest"
      ]
    }
  }
}
```

### Network Isolation (Advanced)

For maximum security, restrict network access to only the required APIs:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network=none",
        "--add-host=sanastot.suomi.fi:$(dig +short sanastot.suomi.fi)",
        "--add-host=tietomallit.suomi.fi:$(dig +short tietomallit.suomi.fi)",
        "--add-host=koodistot.suomi.fi:$(dig +short koodistot.suomi.fi)",
        "-v", "yhteentoimivuusalusta-cache:/app/cache",
        "yhteentoimivuusalusta-mcp:latest"
      ]
    }
  }
}
```

Note: The `--network=none` approach requires resolving IPs at container start time, which may break if IPs change. For most use cases, the default bridge network is sufficient.

## Troubleshooting

### Container won't start

Check Docker is running:
```bash
docker info
```

Check for build errors:
```bash
docker build -t yhteentoimivuusalusta-mcp:latest . 2>&1
```

### MCP not appearing in Claude Desktop

1. Verify the config file path is correct for your OS
2. Check JSON syntax is valid
3. Restart Claude Desktop completely (not just the window)
4. Check Claude Desktop logs for errors

### Permission errors on cache volume

On Linux/macOS, ensure the volume has correct permissions:
```bash
docker volume create yhteentoimivuusalusta-cache
```

### Network timeouts

If API calls timeout, the container may have network issues:
```bash
# Test network connectivity
docker run --rm yhteentoimivuusalusta-mcp:latest python -c "
import httpx
r = httpx.get('https://sanastot.suomi.fi/terminology-api/v2/frontend/search-terminologies?pageSize=1', timeout=10)
print(f'Status: {r.status_code}')
"
```

## Development

### Rebuild after changes

```bash
docker compose build --no-cache
```

### Run tests in container

```bash
docker compose run --rm test
```

### Interactive shell for debugging

```bash
docker run -it --rm --entrypoint /bin/bash yhteentoimivuusalusta-mcp:latest
```

## Security Considerations

The Docker setup provides these security benefits:

| Feature | Benefit |
|---------|---------|
| Non-root user | Container runs as `mcpuser`, not root |
| Read-only filesystem | Prevents malicious writes (except cache) |
| No new privileges | Blocks privilege escalation |
| Resource limits | Prevents resource exhaustion |
| Isolated filesystem | No access to host files |
| Minimal image | `python:3.11-slim` reduces attack surface |

### What the container CAN access:
- Network: `*.suomi.fi` API endpoints (and any other network by default)
- Filesystem: Only `/app/cache` volume

### What the container CANNOT access:
- Host filesystem (except mounted volumes)
- Other Docker containers (isolated network)
- Host processes or system calls (limited by Docker)
