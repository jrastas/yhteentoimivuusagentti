#!/usr/bin/env python3
"""Setup script for Claude Desktop MCP integration.

This script generates or updates the Claude Desktop configuration
to include the Yhteentoimivuusalusta MCP server.

Usage:
    python scripts/setup_claude_desktop.py [--print-only]

Options:
    --print-only    Print the config instead of writing to file
"""

import json
import os
import sys
from pathlib import Path


def get_claude_config_path() -> Path:
    """Get the Claude Desktop config file path for the current OS."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def get_project_dir() -> Path:
    """Get the project directory (parent of scripts/)."""
    return Path(__file__).parent.parent.resolve()


def get_python_path() -> str:
    """Get the Python executable path."""
    # Check for virtual environment
    venv_python = get_project_dir() / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)

    # Windows venv path
    venv_python_win = get_project_dir() / ".venv" / "Scripts" / "python.exe"
    if venv_python_win.exists():
        return str(venv_python_win)

    # Fall back to system Python
    return sys.executable


def generate_mcp_config() -> dict:
    """Generate the MCP server configuration."""
    project_dir = get_project_dir()
    python_path = get_python_path()

    return {
        "yhteentoimivuusalusta": {
            "command": python_path,
            "args": ["-m", "yhteentoimivuusalusta_mcp.server"],
            "cwd": str(project_dir)
        }
    }


def update_claude_config(print_only: bool = False) -> None:
    """Update Claude Desktop configuration with MCP server.

    Args:
        print_only: If True, print config instead of writing.
    """
    config_path = get_claude_config_path()
    mcp_config = generate_mcp_config()

    # Load existing config or create new
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {}

    # Ensure mcpServers key exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add/update our server config
    config["mcpServers"].update(mcp_config)

    # Format output
    config_json = json.dumps(config, indent=2)

    if print_only:
        print("Generated configuration:")
        print("-" * 40)
        print(config_json)
        print("-" * 40)
        print(f"\nConfig file location: {config_path}")
        return

    # Create directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write config
    with open(config_path, "w") as f:
        f.write(config_json)

    print(f"Updated Claude Desktop config: {config_path}")
    print("\nConfiguration added:")
    print(json.dumps(mcp_config, indent=2))
    print("\nPlease restart Claude Desktop for changes to take effect.")


def main():
    """Main entry point."""
    print("Yhteentoimivuusalusta MCP Server - Claude Desktop Setup")
    print("=" * 55)
    print()

    print_only = "--print-only" in sys.argv

    print(f"Project directory: {get_project_dir()}")
    print(f"Python executable: {get_python_path()}")
    print(f"Config file: {get_claude_config_path()}")
    print()

    update_claude_config(print_only=print_only)


if __name__ == "__main__":
    main()
