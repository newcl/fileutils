#!/usr/bin/env python3
"""
Entry point for running deduper as a module: python -m deduper
"""

from .cli_click import main

if __name__ == "__main__":
    main() 