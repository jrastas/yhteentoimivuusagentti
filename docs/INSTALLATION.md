# Installation Guide

Complete guide for installing and configuring the Yhteentoimivuusalusta MCP Server.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Claude Desktop Setup](#claude-desktop-setup)
5. [Verification](#verification)
6. [Upgrading](#upgrading)
7. [Uninstallation](#uninstallation)

---

## Prerequisites

### Required

- **Python 3.11 or higher**
  ```bash
  python --version  # Should show 3.11+
  ```

- **pip or uv package manager**
  ```bash
  pip --version
  # or
  uv --version
  ```

### Optional

- **rapidfuzz** - Improved fuzzy matching performance
- **voikko** - Finnish language lemmatization (requires libvoikko)

---

## Installation Methods

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/yaskael/yhteentoimivuusagentti.git
cd yhteentoimivuusagentti

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .
```

### Method 2: Using uv (Fast)

```bash
git clone https://github.com/yaskael/yhteentoimivuusagentti.git
cd yhteentoimivuusagentti

# Install with uv
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Method 3: Direct pip install

```bash
pip install git+https://github.com/yaskael/yhteentoimivuusagentti.git
```

---

## Optional Dependencies

### Improved Fuzzy Matching

Install rapidfuzz for better fuzzy matching performance:

```bash
pip install rapidfuzz
```

### Finnish NLP Support

For Finnish lemmatization support, install Voikko:

**Ubuntu/Debian:**
```bash
sudo apt-get install libvoikko1 voikko-fi
pip install voikko
```

**macOS:**
```bash
brew install libvoikko
pip install voikko
```

**Windows:**
Download libvoikko from https://voikko.puimula.org/ and add to PATH, then:
```bash
pip install voikko
```

---

## Configuration

### 1. Create Configuration File

```bash
cp config.yaml.example config.yaml
```

### 2. Edit Configuration

```yaml
# config.yaml

# Cache settings
cache:
  enabled: true
  directory: ~/.cache/yhteentoimivuusalusta

# Rate limiting
rate_limit:
  requests_per_second: 10.0

# API endpoints (usually no need to change)
apis:
  sanastot:
    base_url: https://sanastot.suomi.fi/terminology-api/api/v1
    timeout: 30
  tietomallit:
    base_url: https://tietomallit.suomi.fi/datamodel-api/api/v2
    timeout: 30
  koodistot:
    base_url: https://koodistot.suomi.fi/codelist-api/api/v1
    timeout: 30

# Logging
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
```

### 3. Environment Variables (Alternative)

You can also configure via environment variables:

```bash
export YHTEENTOIMIVUUS_CACHE_DIR=~/.cache/yhteentoimivuusalusta
export YHTEENTOIMIVUUS_RATE_LIMIT=10.0
export YHTEENTOIMIVUUS_LOG_LEVEL=INFO
```

---

## Claude Desktop Setup

### 1. Locate Claude Desktop Config

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Add MCP Server Configuration

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "python",
      "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
      "cwd": "/path/to/yhteentoimivuusagentti",
      "env": {
        "PYTHONPATH": "/path/to/yhteentoimivuusagentti/src"
      }
    }
  }
}
```

### 3. Using Virtual Environment

If using a virtual environment:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "/path/to/yhteentoimivuusagentti/.venv/bin/python",
      "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
      "cwd": "/path/to/yhteentoimivuusagentti"
    }
  }
}
```

### 4. Restart Claude Desktop

After editing the config, restart Claude Desktop for changes to take effect.

---

## Verification

### 1. Test Server Startup

```bash
cd /path/to/yhteentoimivuusagentti
python -m yhteentoimivuusalusta_mcp.server
```

The server should start without errors. Press Ctrl+C to stop.

### 2. Run Tests

```bash
pytest tests/ -v
```

All 42 tests should pass.

### 3. Test in Claude Desktop

After configuring Claude Desktop, try asking:

> "Search for the Finnish term 'rakennus' using the yhteentoimivuusalusta tools"

Claude should use the `search_terminology` tool.

---

## Upgrading

### From Git Source

```bash
cd /path/to/yhteentoimivuusagentti
git pull origin main
pip install -e .
```

### Clear Cache After Upgrade

```bash
rm -rf ~/.cache/yhteentoimivuusalusta/*
```

---

## Uninstallation

### 1. Remove Package

```bash
pip uninstall yhteentoimivuusalusta-mcp
```

### 2. Remove Configuration

```bash
rm -rf ~/.cache/yhteentoimivuusalusta
rm /path/to/yhteentoimivuusagentti/config.yaml
```

### 3. Remove from Claude Desktop

Edit `claude_desktop_config.json` and remove the `yhteentoimivuusalusta` entry.

---

## Troubleshooting Installation

### Python Version Error

```
ERROR: This package requires Python 3.11+
```

**Solution:** Install Python 3.11 or higher:
```bash
# Ubuntu
sudo apt install python3.11

# macOS
brew install python@3.11
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:** Reinstall with all dependencies:
```bash
pip install -e . --force-reinstall
```

### Permission Denied

```
PermissionError: [Errno 13] Permission denied: '/path/to/cache'
```

**Solution:** Check cache directory permissions:
```bash
mkdir -p ~/.cache/yhteentoimivuusalusta
chmod 755 ~/.cache/yhteentoimivuusalusta
```

### Claude Desktop Not Finding Server

**Solutions:**
1. Verify the path in `claude_desktop_config.json` is absolute
2. Check Python is in PATH or use absolute path to Python
3. Restart Claude Desktop after config changes

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.
