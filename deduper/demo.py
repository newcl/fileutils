#!/usr/bin/env python3
"""
Demo script for the deduper tool.
Creates test files and demonstrates the functionality.
"""

import tempfile
import os
from pathlib import Path
from deduper.scanner import DuplicateScanner


def create_test_files(temp_dir: Path):
    """Create test files for demonstration."""
    print("Creating test files...")
    
    # Create some unique files
    (temp_dir / "unique1.txt").write_text("This is a unique file with content 1")
    (temp_dir / "unique2.txt").write_text("This is a unique file with content 2")
    
    # Create duplicate files
    duplicate_content = "This is duplicate content that will appear in multiple files"
    (temp_dir / "duplicate1.txt").write_text(duplicate_content)
    (temp_dir / "duplicate2.txt").write_text(duplicate_content)
    (temp_dir / "duplicate3.txt").write_text(duplicate_content)
    
    # Create another set of duplicates
    another_content = "Another set of duplicate content"
    (temp_dir / "copy1.txt").write_text(another_content)
    (temp_dir / "copy2.txt").write_text(another_content)
    
    # Create a subdirectory with more duplicates
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "duplicate1.txt").write_text(duplicate_content)
    (subdir / "unique3.txt").write_text("Unique content in subdirectory")
    
    print(f"Created test files in: {temp_dir}")
    print("Files created:")
    for file_path in temp_dir.rglob("*"):
        if file_path.is_file():
            print(f"  {file_path.relative_to(temp_dir)}")


def demo_hash_comparison(temp_dir: Path):
    """Demonstrate hash-based duplicate detection."""
    print("\n" + "="*50)
    print("DEMO: Hash-based Duplicate Detection")
    print("="*50)
    
    scanner = DuplicateScanner(hash_algorithm="sha256")
    duplicate_groups = scanner.scan([temp_dir], use_byte_comparison=False)
    
    print(f"Found {len(duplicate_groups)} duplicate groups:")
    for i, group in enumerate(duplicate_groups, 1):
        print(f"\nGroup {i} ({len(group)} files):")
        for j, file_path in enumerate(group):
            marker = " [KEEP]" if j == 0 else " [DUPLICATE]"
            print(f"  {j+1}. {file_path.relative_to(temp_dir)}{marker}")


def demo_byte_comparison(temp_dir: Path):
    """Demonstrate byte-by-byte duplicate detection."""
    print("\n" + "="*50)
    print("DEMO: Byte-by-Byte Duplicate Detection")
    print("="*50)
    
    scanner = DuplicateScanner()
    duplicate_groups = scanner.scan([temp_dir], use_byte_comparison=True)
    
    print(f"Found {len(duplicate_groups)} duplicate groups:")
    for i, group in enumerate(duplicate_groups, 1):
        print(f"\nGroup {i} ({len(group)} files):")
        for j, file_path in enumerate(group):
            marker = " [KEEP]" if j == 0 else " [DUPLICATE]"
            print(f"  {j+1}. {file_path.relative_to(temp_dir)}{marker}")


def demo_size_filtering(temp_dir: Path):
    """Demonstrate size filtering."""
    print("\n" + "="*50)
    print("DEMO: Size Filtering")
    print("="*50)
    
    # Create a large file
    large_content = "x" * 1000  # 1000 bytes
    (temp_dir / "large_file.txt").write_text(large_content)
    (temp_dir / "large_file_copy.txt").write_text(large_content)
    
    print("Created large duplicate files (1000 bytes each)")
    
    # Scan with minimum size filter
    scanner = DuplicateScanner(min_size=500)  # Only files >= 500 bytes
    duplicate_groups = scanner.scan([temp_dir])
    
    print(f"Found {len(duplicate_groups)} duplicate groups (files >= 500 bytes):")
    for i, group in enumerate(duplicate_groups, 1):
        print(f"\nGroup {i} ({len(group)} files):")
        for j, file_path in enumerate(group):
            marker = " [KEEP]" if j == 0 else " [DUPLICATE]"
            print(f"  {j+1}. {file_path.relative_to(temp_dir)}{marker}")


def demo_dry_run_purge(temp_dir: Path):
    """Demonstrate dry run purge mode."""
    print("\n" + "="*50)
    print("DEMO: Dry Run Purge Mode")
    print("="*50)
    
    scanner = DuplicateScanner()
    duplicate_groups = scanner.scan([temp_dir])
    
    print("Files that would be removed (dry run):")
    removed_count = scanner.purge_duplicates(duplicate_groups, dry_run=True)
    print(f"\nTotal files that would be removed: {removed_count}")
    print("(No files were actually deleted)")


def main():
    """Run the demo."""
    print("Deduper Tool Demo")
    print("="*50)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        create_test_files(temp_path)
        
        # Run demonstrations
        demo_hash_comparison(temp_path)
        demo_byte_comparison(temp_path)
        demo_size_filtering(temp_path)
        demo_dry_run_purge(temp_path)
        
        print("\n" + "="*50)
        print("Demo completed!")
        print("="*50)
        print("\nTo run the actual CLI tool:")
        print(f"  python -m deduper scan {temp_path}")
        print(f"  python -m deduper scan {temp_path} --all-bytes")
        print(f"  python -m deduper scan {temp_path} --purge --dry-run")


if __name__ == "__main__":
    main() 