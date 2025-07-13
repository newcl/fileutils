#!/usr/bin/env python3
"""
Deduper CLI using Click library - More reliable CLI implementation.
"""

import click
import sys
import os
from pathlib import Path
from typing import List, Optional

from scanner import DuplicateScanner
from utils import setup_logging, get_logger


@click.group()
@click.version_option(version="1.0.0", prog_name="deduper")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.pass_context
def cli(ctx, verbose, quiet):
    """A platform-agnostic CLI tool for finding and managing duplicate files."""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    if quiet:
        log_level = "ERROR"
    
    setup_logging(log_level)
    ctx.ensure_object(dict)
    ctx.obj['logger'] = get_logger(__name__)


@cli.command()
@click.argument('paths', nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option('--all-bytes', is_flag=True, help='Use byte-by-byte comparison instead of hash (more accurate but slower)')
@click.option('--purge', is_flag=True, help='Remove duplicate files, keeping only one copy of each')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file to save results')
@click.option('--hash-algorithm', type=click.Choice(['md5', 'sha1', 'sha256', 'sha512']), default='sha256', help='Hash algorithm to use for comparison')
@click.option('--min-size', type=int, default=0, help='Minimum file size in bytes to consider')
@click.option('--max-size', type=int, help='Maximum file size in bytes to consider')
@click.option('--recursive/--no-recursive', default=True, help='Scan directories recursively')
@click.option('--follow-symlinks', is_flag=True, help='Follow symbolic links')
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually doing it (useful with --purge)')
@click.pass_context
def scan(ctx, paths, all_bytes, purge, output, hash_algorithm, min_size, max_size, recursive, follow_symlinks, dry_run):
    """Scan directories for duplicate files."""
    logger = ctx.obj['logger']
    
    # Create scanner
    scanner = DuplicateScanner(
        hash_algorithm=hash_algorithm,
        min_size=min_size,
        max_size=max_size,
        recursive=recursive,
        follow_symlinks=follow_symlinks
    )
    
    try:
        # Scan for duplicates
        logger.info(f"Scanning {len(paths)} path(s) for duplicates...")
        duplicate_groups = scanner.scan(paths, use_byte_comparison=all_bytes)
        
        if not duplicate_groups:
            click.echo("No duplicate files found.")
            return
        
        # Output results
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                scanner.output_results(duplicate_groups, f)
            click.echo(f"Results saved to: {output}")
        else:
            scanner.output_results(duplicate_groups, sys.stdout)
        
        # Handle purge if requested
        if purge:
            if dry_run:
                click.echo("\n--- DRY RUN MODE ---")
                click.echo("The following files would be removed:")
                scanner.purge_duplicates(duplicate_groups, dry_run=True)
            else:
                click.echo("\nRemoving duplicate files...")
                removed_count = scanner.purge_duplicates(duplicate_groups, dry_run=False)
                click.echo(f"Removed {removed_count} duplicate files.")
    
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the deduper CLI."""
    cli()


if __name__ == "__main__":
    main() 