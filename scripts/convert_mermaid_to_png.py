#!/usr/bin/env python
"""
Convert Mermaid diagram to PNG using a Python-based approach.

This script takes a Mermaid diagram file (.mmd) and converts it to PNG
using the mermaid-cli package (mmdc) via a Node.js subprocess.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    # Check for Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Node.js is not installed or not in PATH.")
        print("Please install Node.js: https://nodejs.org/")
        return False

    # Check for mmdc (Mermaid CLI)
    try:
        subprocess.run(["mmdc", "--version"], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: mermaid-cli is not installed or not in PATH.")
        print("You can install it with: npm install -g @mermaid-js/mermaid-cli")
        return False

    return True


def install_mermaid_cli():
    """Attempt to install mermaid-cli locally."""
    print("Attempting to install mermaid-cli locally...")
    try:
        subprocess.run(["npm", "install", "@mermaid-js/mermaid-cli"], check=True)
        print("mermaid-cli installed successfully!")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Failed to install mermaid-cli.")
        return False


def convert_mermaid_to_png(mmd_path, output_path=None):
    """Convert a Mermaid file to PNG."""
    if not output_path:
        output_path = Path(mmd_path).with_suffix('.png')

    # Try using globally installed mmdc
    try:
        subprocess.run(["mmdc", "-i", mmd_path, "-o", output_path], check=True)
        print(f"Diagram successfully saved to {output_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Could not use global mmdc, trying local installation...")

    # Try using locally installed mmdc
    try:
        local_mmdc = "./node_modules/.bin/mmdc"
        subprocess.run([local_mmdc, "-i", mmd_path, "-o", output_path], check=True)
        print(f"Diagram successfully saved to {output_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Could not convert the diagram using locally installed mmdc.")

    # Try using npx
    try:
        subprocess.run(["npx", "@mermaid-js/mermaid-cli", "-i", mmd_path, "-o", output_path], check=True)
        print(f"Diagram successfully saved to {output_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Could not convert the diagram using npx.")

    print("Failed to convert Mermaid to PNG.")
    return False


def fallback_mermaid_to_png(mmd_path, output_path=None):
    """Provide instructions for using the Mermaid Live Editor as fallback."""
    if not output_path:
        output_path = Path(mmd_path).with_suffix('.png')

    print("\nFallback method:")
    print("1. Go to the Mermaid Live Editor: https://mermaid.live/")
    print(f"2. Open the .mmd file ({mmd_path}) in a text editor")
    print("3. Copy its contents and paste it into the Mermaid Live Editor")
    print("4. Download the PNG from the editor")
    print(f"5. Save it to {output_path}")

    return False


def main():
    """Main function to convert a Mermaid diagram to PNG."""
    if len(sys.argv) < 2:
        print("Usage: python convert_mermaid_to_png.py <path_to_mmd_file> [output_path]")
        return

    mmd_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(mmd_path):
        print(f"Error: File not found - {mmd_path}")
        return

    if not check_dependencies():
        if not install_mermaid_cli():
            fallback_mermaid_to_png(mmd_path, output_path)
            return

    if not convert_mermaid_to_png(mmd_path, output_path):
        fallback_mermaid_to_png(mmd_path, output_path)


if __name__ == "__main__":
    main()
