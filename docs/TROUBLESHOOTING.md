# Troubleshooting Guide

Solutions to common issues with the Yhteentoimivuusalusta MCP Server.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Server Startup Issues](#server-startup-issues)
3. [Claude Desktop Integration](#claude-desktop-integration)
4. [API and Network Issues](#api-and-network-issues)
5. [Performance Issues](#performance-issues)
6. [Tool-Specific Issues](#tool-specific-issues)
7. [Logging and Debugging](#logging-and-debugging)

---

## Installation Issues

### Python Version Too Old

**Error:**
```
ERROR: This package requires Python >=3.11
```

**Solution:**
Install Python 3.11 or higher:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# macOS
brew install python@3.11

# Windows
# Download from python.org
```

Then create a virtual environment with the correct version:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### Missing mcp Package

**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
The mcp package should be installed automatically. If not:

```bash
pip install mcp
```

Or reinstall the project:
```bash
pip install -e . --force-reinstall
```

---

### diskcache Installation Fails

**Error:**
```
ERROR: Could not build wheels for diskcache
```

**Solution:**
Install build dependencies:

```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# macOS
xcode-select --install

# Then retry
pip install diskcache
```

---

## Server Startup Issues

### Server Exits Immediately

**Symptom:** Server starts but exits without error.

**Cause:** MCP servers communicate via stdio and exit when stdin closes.

**Solution:** This is normal behavior. The server should be started by Claude Desktop, not run manually for regular use. For testing:

```bash
# Keep server running for testing
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | python -m yhteentoimivuusalusta_mcp.server
```

---

### Import Error on Startup

**Error:**
```
ImportError: cannot import name 'X' from 'yhteentoimivuusalusta_mcp'
```

**Solution:**
Ensure you're in the project directory and the package is installed:

```bash
cd /path/to/yhteentoimivuusagentti
pip install -e .
```

---

### Configuration File Not Found

**Error:**
```
FileNotFoundError: config.yaml not found
```

**Solution:**
The config file is optional. Create one from the example:

```bash
cp config.yaml.example config.yaml
```

Or the server will use default settings.

---

## Claude Desktop Integration

### Server Not Appearing in Claude

**Symptom:** Claude Desktop doesn't show the MCP tools.

**Solutions:**

1. **Check config file location:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Verify JSON syntax:**
   ```bash
   cat claude_desktop_config.json | python -m json.tool
   ```

3. **Use absolute paths:**
   ```json
   {
     "mcpServers": {
       "yhteentoimivuusalusta": {
         "command": "/usr/bin/python3",
         "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
         "cwd": "/home/user/yhteentoimivuusagentti"
       }
     }
   }
   ```

4. **Restart Claude Desktop** after config changes.

---

### Connection Refused

**Error in Claude:**
```
Failed to connect to MCP server: Connection refused
```

**Solutions:**

1. **Test server manually:**
   ```bash
   python -m yhteentoimivuusalusta_mcp.server
   ```

2. **Check Python path:**
   ```bash
   which python
   # Use this exact path in config
   ```

3. **Check virtual environment:**
   If using venv, point to the venv Python:
   ```json
   {
     "command": "/path/to/project/.venv/bin/python"
   }
   ```

---

### Tools Not Working

**Symptom:** Tools appear but return errors.

**Solutions:**

1. **Check PYTHONPATH:**
   ```json
   {
     "env": {
       "PYTHONPATH": "/path/to/yhteentoimivuusagentti/src"
     }
   }
   ```

2. **Verify dependencies:**
   ```bash
   pip list | grep -E "mcp|httpx|pydantic"
   ```

---

## API and Network Issues

### Connection Timeout

**Error:**
```
httpx.ConnectTimeout: Connection timeout
```

**Causes:**
- Network issues
- API service down
- Firewall blocking

**Solutions:**

1. **Test API directly:**
   ```bash
   curl https://sanastot.suomi.fi/terminology-api/api/v1/frontend/terminologies
   ```

2. **Check firewall/proxy settings**

3. **Increase timeout in config:**
   ```yaml
   apis:
     sanastot:
       timeout: 60
   ```

4. **Use offline mode:** The server will return cached data if available.

---

### Rate Limit Exceeded

**Error:**
```
HTTP 429: Too Many Requests
```

**Solution:**
The server has built-in rate limiting (10 req/sec by default). If you're still hitting limits:

1. **Reduce rate limit:**
   ```yaml
   rate_limit:
     requests_per_second: 5.0
   ```

2. **Wait and retry:** The server automatically retries with backoff.

---

### SSL Certificate Error

**Error:**
```
ssl.SSLCertVerificationError: certificate verify failed
```

**Solutions:**

1. **Update certificates:**
   ```bash
   # macOS
   /Applications/Python\ 3.11/Install\ Certificates.command

   # Linux
   sudo apt install ca-certificates
   ```

2. **Check system time** - certificate validation requires correct time.

---

## Performance Issues

### Slow Responses

**Causes:**
- First request (cache miss)
- Large result sets
- Network latency

**Solutions:**

1. **Enable caching** (enabled by default):
   ```yaml
   cache:
     enabled: true
   ```

2. **Limit results:**
   ```json
   {"max_results": 10}
   ```

3. **Pre-warm cache:** Run common queries once to populate cache.

---

### High Memory Usage

**Cause:** Large cache or many concurrent requests.

**Solutions:**

1. **Clear cache:**
   ```bash
   rm -rf ~/.cache/yhteentoimivuusalusta/*
   ```

2. **Limit cache size** (in config.yaml):
   ```yaml
   cache:
     max_size_mb: 100
   ```

---

### Disk Space Issues

**Cause:** Cache growing too large.

**Solution:**
```bash
# Check cache size
du -sh ~/.cache/yhteentoimivuusalusta

# Clear if needed
rm -rf ~/.cache/yhteentoimivuusalusta/*
```

---

## Tool-Specific Issues

### search_terminology Returns No Results

**Possible causes:**
1. Typo in query
2. Wrong vocabulary_id
3. Term doesn't exist

**Solutions:**
1. Try without vocabulary_id to search all vocabularies
2. Use fuzzy matching (enabled by default)
3. Try related terms or synonyms

---

### validate_terminology Slow on Large Text

**Cause:** Processing many terms against vocabulary.

**Solution:**
Split large documents:
```json
{
  "text": "First 5000 characters...",
  "vocabularies": ["rakymp"]
}
```

---

### get_codes Returns Empty

**Possible causes:**
1. Wrong registry/scheme ID
2. Code list deprecated

**Solution:**
First search for the code list:
```json
{
  "tool": "search_codelist",
  "arguments": {"query": "your search term"}
}
```

---

## Logging and Debugging

### Enable Debug Logging

```yaml
# config.yaml
logging:
  level: DEBUG
```

Or via environment:
```bash
export YHTEENTOIMIVUUS_LOG_LEVEL=DEBUG
```

### View Logs

Logs are written to stderr. When running manually:
```bash
python -m yhteentoimivuusalusta_mcp.server 2>&1 | tee server.log
```

### Common Log Messages

| Message | Meaning |
|---------|---------|
| `Cache hit for...` | Data served from cache |
| `Request failed, retrying...` | Network issue, automatic retry |
| `Offline mode: returning stale cache` | API down, using cached data |
| `Rate limit: waiting...` | Throttling to avoid API limits |

---

## Getting Help

If you can't resolve an issue:

1. **Check existing issues:** https://github.com/yaskael/yhteentoimivuusagentti/issues

2. **Create a new issue** with:
   - Error message
   - Steps to reproduce
   - Python version (`python --version`)
   - OS and version
   - Relevant log output

3. **Include config** (remove any sensitive data)
