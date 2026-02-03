#!/usr/bin/env python3
"""Create an MCPB bundle for Claude Desktop.

This script creates a properly structured .mcpb bundle that can be
installed in Claude Desktop.

Usage:
    python scripts/create_bundle.py
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def get_project_dir() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def create_bundle():
    """Create the .mcpb bundle."""
    project_dir = get_project_dir()
    build_dir = project_dir / "build"
    bundle_dir = build_dir / "bundle"
    server_dir = bundle_dir / "server"

    print("Creating MCPB bundle...")
    print(f"Project directory: {project_dir}")

    # Clean build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)

    bundle_dir.mkdir(parents=True)
    server_dir.mkdir(parents=True)

    # Copy manifest.json
    print("Copying manifest.json...")
    shutil.copy(project_dir / "manifest.json", bundle_dir / "manifest.json")

    # Copy source code
    print("Copying source code...")
    shutil.copytree(
        project_dir / "src" / "yhteentoimivuusalusta_mcp",
        server_dir / "yhteentoimivuusalusta_mcp"
    )

    # Create a simple __main__.py for the server
    main_content = '''"""Entry point for the MCP server."""
import sys
import os

# Add server directory to path
server_dir = os.path.dirname(os.path.abspath(__file__))
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

from yhteentoimivuusalusta_mcp.server import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
    (server_dir / "__main__.py").write_text(main_content)

    # Install dependencies to server/lib
    print("Installing dependencies...")
    lib_dir = server_dir / "lib"
    lib_dir.mkdir(exist_ok=True)

    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "--target", str(lib_dir),
        "--quiet",
        "mcp", "httpx", "pydantic", "diskcache", "pyyaml"
    ], check=True)

    # Update manifest for bundled structure
    manifest_path = bundle_dir / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest["server"]["entry_point"] = "server/__main__.py"
    manifest["server"]["mcp_config"] = {
        "command": "python",
        "args": ["${__dirname}/server/__main__.py"],
        "env": {
            "PYTHONPATH": "${__dirname}/server:${__dirname}/server/lib"
        }
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Create the .mcpb zip file
    print("Creating .mcpb bundle...")
    bundle_name = f"yhteentoimivuusalusta-{manifest['version']}.mcpb"
    bundle_path = build_dir / bundle_name

    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in bundle_dir.rglob('*'):
            if file_path.is_file():
                arc_name = file_path.relative_to(bundle_dir)
                zf.write(file_path, arc_name)

    print(f"\nBundle created: {bundle_path}")
    print(f"Bundle size: {bundle_path.stat().st_size / 1024 / 1024:.2f} MB")

    # Also create unpacked version
    unpacked_dir = build_dir / "unpacked"
    if unpacked_dir.exists():
        shutil.rmtree(unpacked_dir)
    shutil.copytree(bundle_dir, unpacked_dir)
    print(f"Unpacked version: {unpacked_dir}")

    print("\nTo install:")
    print(f"  1. Bundled: Open {bundle_path} with Claude Desktop")
    print(f"  2. Unpacked: Point Claude Desktop to {unpacked_dir}")


if __name__ == "__main__":
    create_bundle()
