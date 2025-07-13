#!/usr/bin/env python3
"""
Standalone deduper executable script.
This can be run directly: python deduper.py scan /path/to/directory
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import our modules
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import our modules
from cli_click import main

if __name__ == "__main__":
    main() 