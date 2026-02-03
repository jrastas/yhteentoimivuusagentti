# Contributing Guide

Thank you for your interest in contributing to the Yhteentoimivuusalusta MCP Server!

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Submitting Changes](#submitting-changes)
8. [Adding New Tools](#adding-new-tools)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- A GitHub account

### Types of Contributions

- **Bug fixes:** Fix issues in existing functionality
- **New features:** Add new tools or capabilities
- **Documentation:** Improve docs, examples, translations
- **Tests:** Add or improve test coverage
- **Performance:** Optimize existing code

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-USERNAME/yhteentoimivuusagentti.git
cd yhteentoimivuusagentti
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
# or if dev extras aren't defined:
pip install -e .
pip install pytest pytest-asyncio ruff mypy
```

### 4. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

---

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Follow the project structure:

```
src/yhteentoimivuusalusta_mcp/
├── server.py          # MCP server and tool routing
├── tools/             # Tool implementations
│   ├── terminology.py
│   ├── datamodel.py
│   ├── codelist.py
│   ├── validation.py
│   └── unified.py
├── clients/           # API clients
│   ├── base.py
│   ├── sanastot.py
│   ├── tietomallit.py
│   └── koodistot.py
├── models/            # Pydantic models
│   └── schemas.py
└── utils/             # Utilities
    ├── cache.py
    ├── config.py
    └── fuzzy.py
```

### 3. Write Tests

Add tests for new functionality in the `tests/` directory.

### 4. Update Documentation

- Update relevant docs in `docs/`
- Update `CLAUDE.md` if adding new tools
- Add docstrings to new functions

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Tests

```bash
# Single file
pytest tests/test_tools/test_terminology.py -v

# Single test
pytest tests/test_tools/test_terminology.py::test_search_terminology -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=src/yhteentoimivuusalusta_mcp --cov-report=html
```

### Test Requirements

- All tests must pass before submitting
- New features should have test coverage
- Maintain or improve existing coverage

---

## Code Style

### Formatting

We use `ruff` for formatting and linting:

```bash
# Format code
ruff format src/ tests/

# Check for issues
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

### Type Hints

Use type hints for all function signatures:

```python
async def search_terminology(
    client: SanastotClient,
    query: str,
    vocabulary_id: str | None = None,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search for terminology.

    Args:
        client: The Sanastot API client.
        query: Search query string.
        vocabulary_id: Optional vocabulary filter.
        max_results: Maximum results to return.

    Returns:
        Dictionary with search results.
    """
    ...
```

### Type Checking

```bash
pip install mypy
mypy src/yhteentoimivuusalusta_mcp
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> dict:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
    """
```

---

## Submitting Changes

### 1. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add new search filter for vocabulary status

- Add status parameter to search_terminology
- Update tests for new parameter
- Update API_REFERENCE.md"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Adding tests
- `refactor:` Code change that neither fixes nor adds
- `perf:` Performance improvement

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (if UI-related)

### 4. Address Review Feedback

- Respond to all comments
- Make requested changes
- Push additional commits

---

## Adding New Tools

### 1. Define the Tool

Add tool definition in `server.py`:

```python
Tool(
    name="your_tool_name",
    description="Clear description of what the tool does.",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description",
            },
        },
        "required": ["param1"],
    },
),
```

### 2. Implement the Tool

Create or add to a file in `tools/`:

```python
# tools/your_module.py

async def your_tool_name(
    client: SomeClient,
    param1: str,
) -> dict[str, Any]:
    """Tool implementation.

    Args:
        client: API client to use.
        param1: Input parameter.

    Returns:
        Result dictionary.
    """
    # Implementation
    result = await client.some_method(param1)
    return {
        "status": "success",
        "data": result,
    }
```

### 3. Add Tool Handler

In `server.py`, add the handler in `_handle_tool_call`:

```python
elif name == "your_tool_name":
    validate_required(arguments, "param1")
    return await your_tool_name(
        client=self.some_client,
        param1=arguments["param1"].strip(),
    )
```

### 4. Add Tests

```python
# tests/test_tools/test_your_module.py

import pytest
from yhteentoimivuusalusta_mcp.tools.your_module import your_tool_name

@pytest.fixture
def mock_client():
    # Create mock client
    ...

@pytest.mark.asyncio
async def test_your_tool_name(mock_client):
    result = await your_tool_name(
        client=mock_client,
        param1="test",
    )
    assert result["status"] == "success"
```

### 5. Update Documentation

- Add to `CLAUDE.md` tool list
- Add to `docs/API_REFERENCE.md`
- Add examples to `docs/USAGE.md`

---

## Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Review the codebase for patterns

Thank you for contributing!
