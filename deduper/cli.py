#!/usr/bin/env python3
"""
Deduper CLI - Main entry point for the deduper command-line tool.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from .scanner import DuplicateScanner
from .utils import setup_logging, get_logger


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="deduper",
        description="A platform-agnostic CLI tool for finding and managing duplicate files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deduper scan /path/to/directory                    # Scan for duplicates using hash
  deduper scan /path1 /path2 --all-bytes            # Use byte-by-byte comparison
  deduper scan /path/to/directory --purge           # Remove duplicates, keep one copy
  deduper scan /path/to/directory --output report.txt # Save results to file
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="deduper 1.0.0"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan directories for duplicate files",
        description="Scan one or more directories to find duplicate files using hash comparison or byte-by-byte analysis."
    )
    
    scan_parser.add_argument(
        "paths",
        nargs="+",
        help="Directories or files to scan for duplicates"
    )
    
    scan_parser.add_argument(
        "--all-bytes",
        action="store_true",
        help="Use byte-by-byte comparison instead of hash (more accurate but slower)"
    )
    
    scan_parser.add_argument(
        "--purge",
        action="store_true",
        help="Remove duplicate files, keeping only one copy of each"
    )
    
    scan_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file to save results (default: stdout)"
    )
    
    scan_parser.add_argument(
        "--hash-algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="Hash algorithm to use for comparison (default: sha256)"
    )
    
    scan_parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Minimum file size in bytes to consider (default: 0)"
    )
    
    scan_parser.add_argument(
        "--max-size",
        type=int,
        help="Maximum file size in bytes to consider (default: no limit)"
    )
    
    scan_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="Scan directories recursively (default: True)"
    )
    
    scan_parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Do not scan directories recursively"
    )
    
    scan_parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links"
    )
    
    scan_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it (useful with --purge)"
    )
    
    return parser


def validate_paths(paths: List[str]) -> List[Path]:
    """Validate and convert paths to Path objects."""
    valid_paths = []
    
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Warning: Path does not exist: {path}", file=sys.stderr)
            continue
        valid_paths.append(path)
    
    if not valid_paths:
        print("Error: No valid paths provided", file=sys.stderr)
        sys.exit(1)
    
    return valid_paths


def main():
    """Main entry point for the deduper CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    if args.quiet:
        log_level = "ERROR"
    
    setup_logging(log_level)
    logger = get_logger(__name__)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "scan":
        # Validate paths
        paths = validate_paths(args.paths)
        
        # Create scanner
        scanner = DuplicateScanner(
            hash_algorithm=args.hash_algorithm,
            min_size=args.min_size,
            max_size=args.max_size,
            recursive=args.recursive,
            follow_symlinks=args.follow_symlinks
        )
        
        try:
            # Scan for duplicates
            logger.info(f"Scanning {len(paths)} path(s) for duplicates...")
            duplicate_groups = scanner.scan(paths, use_byte_comparison=args.all_bytes)
            
            if not duplicate_groups:
                print("No duplicate files found.")
                return
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w', encoding='utf-8') as f:
                    scanner.output_results(duplicate_groups, f)
                print(f"Results saved to: {output_path}")
            else:
                scanner.output_results(duplicate_groups, sys.stdout)
            
            # Handle purge if requested
            if args.purge:
                if args.dry_run:
                    print("\n--- DRY RUN MODE ---")
                    print("The following files would be removed:")
                    scanner.purge_duplicates(duplicate_groups, dry_run=True)
                else:
                    print("\nRemoving duplicate files...")
                    removed_count = scanner.purge_duplicates(duplicate_groups, dry_run=False)
                    print(f"Removed {removed_count} duplicate files.")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main() 