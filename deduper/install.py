#!/usr/bin/env python3
"""
Simple installation script for the deduper tool.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_deduper():
    """Install the deduper package."""
    print("Installing deduper...")
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    try:
        # Install the package in development mode
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", str(script_dir)
        ])
        print("✅ deduper installed successfully!")
        print("\nYou can now use the tool with:")
        print("  deduper scan /path/to/directory")
        print("  python -m deduper scan /path/to/directory")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    
    return True


def uninstall_deduper():
    """Uninstall the deduper package."""
    print("Uninstalling deduper...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "uninstall", "-y", "deduper"
        ])
        print("✅ deduper uninstalled successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Uninstallation failed: {e}")
        return False
    
    return True


def main():
    """Main installation function."""
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_deduper()
    else:
        install_deduper()


if __name__ == "__main__":
    main() 