"""
CLI interface for the deduper tool.
"""

import click
from pathlib import Path
from .core import (
    find_duplicates,
    delete_duplicates,
    print_duplicate_groups
)


@click.group()
@click.version_option()
def main():
    """Deduper CLI - Find and manage duplicate files."""
    pass


@main.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--delete', is_flag=True, help='Delete duplicate files, keeping only one copy')
def scan(folder: Path, delete: bool):
    """Scan a folder for duplicate files using hash comparison with byte-by-byte verification."""
    click.echo(f"Scanning folder: {folder}")
    click.echo("Using hash-based comparison with byte-by-byte verification...")
    
    duplicate_groups = find_duplicates(folder)
    
    if delete:
        delete_duplicates(duplicate_groups, dry_run=False)
    else:
        print_duplicate_groups(duplicate_groups)


if __name__ == '__main__':
    main() 