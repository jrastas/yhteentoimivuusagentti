# Security Policy

## Overview

This document describes the security considerations, findings, and best practices for the Yhteentoimivuusalusta MCP Server.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Model

### Architecture

The MCP server operates as a **local service** that:
1. Runs on the user's machine (or in a Docker container)
2. Communicates with Claude Desktop via stdio (stdin/stdout)
3. Makes HTTPS requests to Finnish government APIs
4. Stores cached data locally

### Trust Boundaries

**Option A: Direct Execution (Standard)**
```
┌─────────────────────────────────────────────────────────────┐
│  User's Machine (Trusted)                                    │
│  ┌─────────────┐     stdio      ┌──────────────────────┐   │
│  │   Claude    │◄──────────────►│  MCP Server          │   │
│  │   Desktop   │                │  (yhteentoimivuusalusta)│ │
│  └─────────────┘                └──────────┬───────────┘   │
│                                            │                │
│                              ┌─────────────┴────────────┐  │
│                              │  Local Cache (~/.cache)  │  │
│                              └──────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────┘
                                   │ HTTPS
                    ┌──────────────┴──────────────┐
                    │  Finnish Government APIs     │
                    │  (sanastot.suomi.fi, etc.)  │
                    └─────────────────────────────┘
```

**Option B: Docker Execution (Recommended for Enhanced Security)**
```
┌─────────────────────────────────────────────────────────────┐
│  User's Machine                                              │
│  ┌─────────────┐     stdio      ┌───────────────────────┐  │
│  │   Claude    │◄──────────────►│  Docker Container     │  │
│  │   Desktop   │                │  ┌─────────────────┐  │  │
│  └─────────────┘                │  │  MCP Server     │  │  │
│                                 │  │  (non-root)     │  │  │
│                                 │  └────────┬────────┘  │  │
│                                 │           │           │  │
│                                 │  ┌────────┴────────┐  │  │
│                                 │  │ /app/cache vol  │  │  │
│                                 │  └─────────────────┘  │  │
│                                 └───────────┬───────────┘  │
└─────────────────────────────────────────────┬──────────────┘
                                              │ HTTPS
                               ┌──────────────┴──────────────┐
                               │  Finnish Government APIs     │
                               │  (*.suomi.fi)                │
                               └─────────────────────────────┘
```

## Security Review Findings

### Positive Findings

#### 1. Input Validation ✅
- All tool parameters are validated before use
- Required parameters are checked with clear error messages
- String inputs are stripped of whitespace
- Maximum result limits are enforced (capped at 1000)
- Text length is limited to prevent resource exhaustion (50,000 chars max)

**Location:** `src/yhteentoimivuusalusta_mcp/server.py:56-113`

```python
def validate_required(arguments, *required_params):
    """Validates required parameters are present and non-empty."""
    ...

def validate_max_results(arguments, param="max_results"):
    """Validates and caps max_results to 1000."""
    ...

def validate_text_length(arguments, param, max_length=10000):
    """Validates text length to prevent resource exhaustion."""
    ...
```

#### 2. No Code Injection Vectors ✅
- No use of `eval()`, `exec()`, or `compile()`
- No shell command execution (`subprocess`, `os.system`)
- No dynamic code loading from user input

#### 3. Safe Configuration Loading ✅
- Uses `yaml.safe_load()` instead of `yaml.load()`
- Prevents YAML deserialization attacks

**Location:** `src/yhteentoimivuusalusta_mcp/utils/config.py:98`

#### 4. HTTPS for All External Communications ✅
- All API endpoints use HTTPS
- httpx handles SSL/TLS certificate verification
- No option to disable certificate verification

**Hardcoded safe URLs:**
- `https://sanastot.suomi.fi/terminology-api` (v2 endpoints)
- `https://tietomallit.suomi.fi/datamodel-api` (v2 endpoints)
- `https://koodistot.suomi.fi/codelist-api/api/v1`

#### 5. Rate Limiting ✅
- Token bucket algorithm prevents API abuse
- Default: 10 requests per second
- Shared across all API clients

**Location:** `src/yhteentoimivuusalusta_mcp/clients/base.py:15-37`

#### 6. No Sensitive Data Storage ✅
- No authentication credentials stored
- No personal data collected
- Cache contains only public API responses

### Areas of Note

#### 1. Cache Storage (Low Risk)

**Finding:** diskcache uses Python pickle for serialization internally.

**Risk:** Pickle deserialization can execute arbitrary code if an attacker can modify cache files.

**Mitigations:**
- Cache is stored in user's home directory with standard permissions
- Cache only contains API responses from trusted government APIs
- Local attacker with file access already has greater capabilities

**Recommendation:** Ensure cache directory permissions are restricted to the user:
```bash
chmod 700 ~/.cache/yhteentoimivuusalusta
```

#### 2. MD5 Hash Usage (Informational)

**Finding:** MD5 is used to hash long cache keys.

**Location:** `src/yhteentoimivuusalusta_mcp/utils/cache.py:72`

**Risk:** None - MD5 is used only for key generation, not cryptographic security.

#### 3. No Authentication (By Design)

**Finding:** The MCP server has no authentication mechanism.

**Risk:** Any process that can connect via stdio can use the server.

**Mitigation:** This is by design - security relies on:
- Claude Desktop's process isolation
- Operating system user permissions
- Local-only operation (no network listeners)

#### 4. Configuration File Paths (Low Risk)

**Finding:** Configuration can be loaded from multiple paths including:
- Current directory (`./config.yaml`)
- User config (`~/.config/yhteentoimivuusalusta/config.yaml`)
- System config (`/etc/yhteentoimivuusalusta/config.yaml`)
- Environment variable (`YHTEENTOIMIVUUSALUSTA_CONFIG`)

**Risk:** Attacker with write access to these paths could modify configuration.

**Mitigations:**
- Configuration only affects API endpoints and caching behavior
- No credential storage in configuration
- Standard file permission model applies

#### 5. Error Information Disclosure (Low Risk)

**Finding:** Error messages include tool arguments in responses.

**Location:** `src/yhteentoimivuusalusta_mcp/server.py:547-548`

**Risk:** Query terms and parameters are visible in error responses.

**Mitigation:** All data flows stay within the local Claude session.

### Not Applicable

The following common vulnerabilities are **not applicable** to this project:

| Vulnerability | Reason |
|---------------|--------|
| SQL Injection | No database access |
| XSS | No web interface |
| CSRF | No web interface |
| Path Traversal | No file path handling from user input |
| SSRF | URLs are hardcoded to government APIs |
| Authentication Bypass | No authentication by design |
| Session Hijacking | No sessions |

## Docker Sandboxing (Recommended)

For enhanced security, run the MCP server in a Docker container. This provides:

| Security Feature | Benefit |
|-----------------|---------|
| **Filesystem isolation** | Container cannot access host files |
| **Non-root execution** | Runs as `mcpuser`, not root |
| **Resource limits** | Memory/CPU caps prevent resource exhaustion |
| **Network control** | Can restrict to only required APIs |
| **Read-only filesystem** | Prevents malicious writes (except cache volume) |
| **Minimal image** | `python:3.11-slim` reduces attack surface |

### Docker Setup

```bash
# Build the container
docker build -t yhteentoimivuusalusta-mcp:latest .

# Configure Claude Desktop to use Docker
# See docs/DOCKER.md for full instructions
```

### Docker Security Configuration

For maximum security, add resource limits:

```json
{
  "mcpServers": {
    "yhteentoimivuusalusta": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
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

See [docs/DOCKER.md](docs/DOCKER.md) for complete Docker setup instructions.

## Security Best Practices

### For Users

1. **Use Docker for sandboxed execution** (Recommended)
   ```bash
   docker build -t yhteentoimivuusalusta-mcp:latest .
   # Configure Claude Desktop per docs/DOCKER.md
   ```

2. **Keep software updated**
   ```bash
   cd yhteentoimivuusagentti
   git pull origin main
   pip install -e .
   # Or rebuild Docker image
   docker build --no-cache -t yhteentoimivuusalusta-mcp:latest .
   ```

3. **Protect configuration files**
   ```bash
   chmod 600 config.yaml
   chmod 700 ~/.cache/yhteentoimivuusalusta
   ```

4. **Review cache contents periodically**
   ```bash
   # Clear cache if needed
   rm -rf ~/.cache/yhteentoimivuusalusta/*
   # Or for Docker
   docker volume rm yhteentoimivuusalusta-cache
   ```

5. **Run in isolated environment**
   - Use Docker (preferred) or virtual environments
   - Don't run as root

### For Developers

1. **Never add `eval()` or `exec()`**
2. **Always use `yaml.safe_load()`**
3. **Validate all user inputs**
4. **Keep dependencies updated**
5. **Don't store credentials in code or config**

## Dependency Security

### Direct Dependencies

| Package | Purpose | Security Notes |
|---------|---------|----------------|
| mcp | MCP protocol | Official Anthropic SDK |
| httpx | HTTP client | Handles TLS properly |
| pydantic | Data validation | Input validation |
| diskcache | Caching | Uses pickle (local only) |
| PyYAML | Config loading | Use safe_load only |

### Updating Dependencies

```bash
pip install --upgrade mcp httpx pydantic diskcache pyyaml
```

### Checking for Vulnerabilities

```bash
pip install safety
safety check
```

## Reporting Security Issues

### Private Disclosure

For security vulnerabilities, please **do not** open a public issue.

Instead, report privately:
1. Email the maintainer directly
2. Use GitHub's private vulnerability reporting (if enabled)

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial response:** 48 hours
- **Assessment:** 7 days
- **Fix (if applicable):** 30 days

## Security Changelog

### v0.1.1 (Docker Sandboxing)

- Added Docker support for sandboxed execution
- Non-root container user (`mcpuser`)
- Resource limits (memory, CPU) support
- Read-only filesystem option
- Isolated cache via Docker volume
- Updated API endpoints to v2 (Sanastot, Tietomallit)

### v0.1.0 (Initial Release)

- Implemented input validation for all tool parameters
- Added rate limiting (10 req/sec)
- Used HTTPS for all external communications
- Used yaml.safe_load for configuration
- Added text length limits for validation tools

## Future Security Enhancements

Potential improvements for future versions:

1. **Signed cache entries** - Prevent tampering with cached data
2. **Request logging** - Audit trail for tool usage
3. **Configuration validation** - Stricter config file validation
4. **Dependency pinning** - Lock dependency versions (see `uv.lock`)
5. **SBOM generation** - Software Bill of Materials for supply chain security
6. **Network policy** - Docker network restrictions to only allow `*.suomi.fi`
7. **seccomp profiles** - Restrict system calls in Docker container
