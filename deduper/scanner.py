"""
Duplicate Scanner - Core functionality for finding duplicate files.
"""

import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, TextIO
import logging

from .utils import get_logger, format_file_size


class DuplicateScanner:
    """Scanner for finding duplicate files using hash or byte-by-byte comparison."""
    
    def __init__(
        self,
        hash_algorithm: str = "sha256",
        min_size: int = 0,
        max_size: Optional[int] = None,
        recursive: bool = True,
        follow_symlinks: bool = False,
        chunk_size: int = 8192
    ):
        """
        Initialize the duplicate scanner.
        
        Args:
            hash_algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', 'sha512')
            min_size: Minimum file size in bytes to consider
            max_size: Maximum file size in bytes to consider
            recursive: Whether to scan directories recursively
            follow_symlinks: Whether to follow symbolic links
            chunk_size: Size of chunks to read when calculating hashes
        """
        self.hash_algorithm = hash_algorithm
        self.min_size = min_size
        self.max_size = max_size
        self.recursive = recursive
        self.follow_symlinks = follow_symlinks
        self.chunk_size = chunk_size
        self.logger = get_logger(__name__)
        
        # Validate hash algorithm
        if hash_algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")
    
    def scan(self, paths: List[Path], use_byte_comparison: bool = False) -> List[List[Path]]:
        """
        Scan paths for duplicate files.
        
        Args:
            paths: List of paths to scan
            use_byte_comparison: Whether to use byte-by-byte comparison instead of hash
            
        Returns:
            List of duplicate groups, where each group is a list of duplicate file paths
        """
        self.logger.info(f"Starting scan of {len(paths)} path(s)")
        self.logger.info(f"Using {'byte-by-byte' if use_byte_comparison else 'hash'} comparison")
        
        # Collect all files
        files = self._collect_files(paths)
        self.logger.info(f"Found {len(files)} files to analyze")
        
        if not files:
            return []
        
        # Group files by size first (quick filter)
        size_groups = self._group_by_size(files)
        self.logger.info(f"Files grouped into {len(size_groups)} size groups")
        
        # Find duplicates within each size group
        duplicate_groups = []
        
        for size, file_list in size_groups.items():
            if len(file_list) < 2:
                continue  # No duplicates possible
            
            self.logger.debug(f"Analyzing {len(file_list)} files of size {format_file_size(size)}")
            
            if use_byte_comparison:
                groups = self._find_duplicates_byte_comparison(file_list)
            else:
                groups = self._find_duplicates_hash(file_list)
            
            duplicate_groups.extend(groups)
        
        self.logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        return duplicate_groups
    
    def _collect_files(self, paths: List[Path]) -> List[Path]:
        """Collect all files from the given paths."""
        files = []
        
        for path in paths:
            if path.is_file():
                if self._should_include_file(path):
                    files.append(path)
            elif path.is_dir():
                if self.recursive:
                    files.extend(self._scan_directory_recursive(path))
                else:
                    files.extend([f for f in path.iterdir() if f.is_file() and self._should_include_file(f)])
        
        return files
    
    def _scan_directory_recursive(self, directory: Path) -> List[Path]:
        """Recursively scan a directory for files."""
        files = []
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    if self._should_include_file(item):
                        files.append(item)
                elif item.is_dir():
                    if self.follow_symlinks or not item.is_symlink():
                        files.extend(self._scan_directory_recursive(item))
        except PermissionError:
            self.logger.warning(f"Permission denied accessing directory: {directory}")
        except OSError as e:
            self.logger.warning(f"Error accessing directory {directory}: {e}")
        
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in the scan."""
        try:
            # Check if it's a regular file
            if not file_path.is_file():
                return False
            
            # Check symlink handling
            if file_path.is_symlink() and not self.follow_symlinks:
                return False
            
            # Get file size
            stat = file_path.stat()
            size = stat.st_size
            
            # Check size constraints
            if size < self.min_size:
                return False
            
            if self.max_size and size > self.max_size:
                return False
            
            return True
            
        except (OSError, PermissionError):
            self.logger.debug(f"Could not access file: {file_path}")
            return False
    
    def _group_by_size(self, files: List[Path]) -> Dict[int, List[Path]]:
        """Group files by their size."""
        size_groups = defaultdict(list)
        
        for file_path in files:
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
            except OSError:
                self.logger.debug(f"Could not get size for file: {file_path}")
                continue
        
        return dict(size_groups)
    
    def _find_duplicates_hash(self, files: List[Path]) -> List[List[Path]]:
        """Find duplicates using hash comparison."""
        hash_groups = defaultdict(list)
        
        for file_path in files:
            try:
                file_hash = self._calculate_file_hash(file_path)
                hash_groups[file_hash].append(file_path)
            except OSError as e:
                self.logger.warning(f"Could not calculate hash for {file_path}: {e}")
                continue
        
        # Return only groups with more than one file
        return [group for group in hash_groups.values() if len(group) > 1]
    
    def _find_duplicates_byte_comparison(self, files: List[Path]) -> List[List[Path]]:
        """Find duplicates using byte-by-byte comparison."""
        if len(files) < 2:
            return []
        
        # Start with the first file as a reference
        duplicate_groups = []
        processed_files = set()
        
        for i, reference_file in enumerate(files):
            if reference_file in processed_files:
                continue
            
            current_group = [reference_file]
            processed_files.add(reference_file)
            
            # Compare with remaining files
            for j in range(i + 1, len(files)):
                candidate_file = files[j]
                if candidate_file in processed_files:
                    continue
                
                try:
                    if self._files_are_identical(reference_file, candidate_file):
                        current_group.append(candidate_file)
                        processed_files.add(candidate_file)
                except OSError as e:
                    self.logger.warning(f"Could not compare {reference_file} with {candidate_file}: {e}")
                    continue
            
            # Only add groups with duplicates
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
        
        return duplicate_groups
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of a file."""
        hash_obj = hashlib.new(self.hash_algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
        except OSError as e:
            raise OSError(f"Could not read file {file_path}: {e}")
        
        return hash_obj.hexdigest()
    
    def _files_are_identical(self, file1: Path, file2: Path) -> bool:
        """Compare two files byte by byte."""
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                while True:
                    chunk1 = f1.read(self.chunk_size)
                    chunk2 = f2.read(self.chunk_size)
                    
                    if chunk1 != chunk2:
                        return False
                    
                    if not chunk1:  # Both files ended
                        return True
        except OSError as e:
            raise OSError(f"Could not compare files {file1} and {file2}: {e}")
    
    def output_results(self, duplicate_groups: List[List[Path]], output: TextIO = sys.stdout):
        """Output duplicate groups in a readable format."""
        if not duplicate_groups:
            output.write("No duplicate files found.\n")
            return
        
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        total_space_wasted = sum(
            (len(group) - 1) * group[0].stat().st_size 
            for group in duplicate_groups
        )
        
        output.write(f"\nFound {len(duplicate_groups)} duplicate groups with {total_duplicates} duplicate files.\n")
        output.write(f"Total space that could be saved: {format_file_size(total_space_wasted)}\n\n")
        
        for i, group in enumerate(duplicate_groups, 1):
            file_size = group[0].stat().st_size
            space_wasted = (len(group) - 1) * file_size
            
            output.write(f"Group {i} ({len(group)} files, {format_file_size(file_size)} each):\n")
            output.write(f"  Space wasted: {format_file_size(space_wasted)}\n")
            
            for j, file_path in enumerate(group):
                marker = " [KEEP]" if j == 0 else " [DUPLICATE]"
                output.write(f"  {j+1}. {file_path}{marker}\n")
            
            output.write("\n")
    
    def purge_duplicates(self, duplicate_groups: List[List[Path]], dry_run: bool = False) -> int:
        """
        Remove duplicate files, keeping only the first file in each group.
        
        Args:
            duplicate_groups: List of duplicate groups
            dry_run: If True, only show what would be deleted without actually deleting
            
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        for group in duplicate_groups:
            # Keep the first file, remove the rest
            files_to_remove = group[1:]
            
            for file_path in files_to_remove:
                try:
                    if dry_run:
                        print(f"  Would remove: {file_path}")
                    else:
                        file_path.unlink()
                        print(f"  Removed: {file_path}")
                        removed_count += 1
                except OSError as e:
                    print(f"  Error removing {file_path}: {e}", file=sys.stderr)
        
        return removed_count 