"""
Core deduplication logic for the deduper CLI tool.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
import click


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except (IOError, OSError) as e:
        click.echo(f"Error reading file {file_path}: {e}", err=True)
        return None


def files_are_identical(file1: Path, file2: Path, chunk_size: int = 8192) -> bool:
    """Compare two files byte by byte."""
    try:
        if file1.stat().st_size != file2.stat().st_size:
            return False
        
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                
                if chunk1 != chunk2:
                    return False
                
                if not chunk1:  # End of file
                    break
        
        return True
    except (IOError, OSError) as e:
        click.echo(f"Error comparing files {file1} and {file2}: {e}", err=True)
        return False


def verify_duplicates_with_byte_comparison(hash_groups: Dict[str, List[Path]]) -> List[List[Path]]:
    """Verify hash-based duplicates with byte-by-byte comparison to eliminate false positives."""
    verified_groups = []
    
    for hash_val, files in hash_groups.items():
        if len(files) <= 1:
            continue
            
        # Group files that are actually identical by byte comparison
        current_groups = []
        processed_files = set()
        
        for i, file1 in enumerate(files):
            if file1 in processed_files:
                continue
                
            current_group = [file1]
            processed_files.add(file1)
            
            for file2 in files[i+1:]:
                if file2 in processed_files:
                    continue
                    
                if files_are_identical(file1, file2):
                    current_group.append(file2)
                    processed_files.add(file2)
            
            if len(current_group) > 1:
                current_groups.append(current_group)
        
        verified_groups.extend(current_groups)
    
    return verified_groups


def find_duplicates(folder_path: Path) -> List[List[Path]]:
    """Find duplicate files using hash comparison with byte-by-byte verification."""
    hash_groups: Dict[str, List[Path]] = {}
    
    # First pass: group files by hash
    for file_path in folder_path.rglob("*"):
        if file_path.is_file():
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_path)
    
    # Second pass: verify duplicates with byte-by-byte comparison
    verified_groups = verify_duplicates_with_byte_comparison(hash_groups)
    
    return verified_groups


def delete_duplicates(duplicate_groups: List[List[Path]], dry_run: bool = True) -> None:
    """Delete duplicate files, keeping the file with the shortest name in each group."""
    for group in duplicate_groups:
        if len(group) <= 1:
            continue
            
        # Find the file with the shortest name
        # If multiple files have the same name length, keep the first one
        shortest_name_file = min(group, key=lambda f: len(f.name))
        files_to_delete = [f for f in group if f != shortest_name_file]
        
        if dry_run:
            click.echo(f"\nDuplicate group (would delete {len(files_to_delete)} files):")
            click.echo(f"  Keep: {shortest_name_file} (shortest name: {len(shortest_name_file.name)} chars)")
            for file_to_delete in files_to_delete:
                click.echo(f"  Delete: {file_to_delete} ({len(file_to_delete.name)} chars)")
        else:
            click.echo(f"\nDeleting {len(files_to_delete)} duplicate files:")
            click.echo(f"  Keeping: {shortest_name_file} (shortest name)")
            for file_to_delete in files_to_delete:
                try:
                    file_to_delete.unlink()
                    click.echo(f"  Deleted: {file_to_delete}")
                except OSError as e:
                    click.echo(f"  Error deleting {file_to_delete}: {e}", err=True)


def print_duplicate_groups(duplicate_groups: List[List[Path]]) -> None:
    """Print duplicate file groups."""
    if not duplicate_groups:
        click.echo("No duplicate files found.")
        return
    
    click.echo(f"\nFound {len(duplicate_groups)} duplicate group(s):")
    total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
    click.echo(f"Total duplicate files: {total_duplicates}")
    
    for i, group in enumerate(duplicate_groups, 1):
        click.echo(f"\nGroup {i} ({len(group)} files):")
        # Find the file with the shortest name to mark it
        shortest_name_file = min(group, key=lambda f: len(f.name))
        for file_path in group:
            if file_path == shortest_name_file:
                click.echo(f"  {file_path} (shortest name - would be kept)")
            else:
                click.echo(f"  {file_path}") 