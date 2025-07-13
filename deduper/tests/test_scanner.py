"""
Unit tests for the DuplicateScanner class.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from deduper.scanner import DuplicateScanner
from deduper.utils import format_file_size


class TestDuplicateScanner:
    """Test cases for DuplicateScanner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = DuplicateScanner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_defaults(self):
        """Test scanner initialization with default values."""
        scanner = DuplicateScanner()
        assert scanner.hash_algorithm == "sha256"
        assert scanner.min_size == 0
        assert scanner.max_size is None
        assert scanner.recursive is True
        assert scanner.follow_symlinks is False
        assert scanner.chunk_size == 8192
    
    def test_init_custom_values(self):
        """Test scanner initialization with custom values."""
        scanner = DuplicateScanner(
            hash_algorithm="md5",
            min_size=1024,
            max_size=1048576,
            recursive=False,
            follow_symlinks=True,
            chunk_size=4096
        )
        assert scanner.hash_algorithm == "md5"
        assert scanner.min_size == 1024
        assert scanner.max_size == 1048576
        assert scanner.recursive is False
        assert scanner.follow_symlinks is True
        assert scanner.chunk_size == 4096
    
    def test_init_invalid_hash_algorithm(self):
        """Test that invalid hash algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            DuplicateScanner(hash_algorithm="invalid")
    
    def test_should_include_file(self):
        """Test file inclusion logic."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        # Test basic inclusion
        assert self.scanner._should_include_file(test_file) is True
        
        # Test size filtering
        scanner = DuplicateScanner(min_size=100)
        assert scanner._should_include_file(test_file) is False
        
        scanner = DuplicateScanner(max_size=5)
        assert scanner._should_include_file(test_file) is False
    
    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        # Create a test file with known content
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        # Test SHA-256 hash
        hash_result = self.scanner._calculate_file_hash(test_file)
        assert len(hash_result) == 64  # SHA-256 hex digest length
        
        # Test MD5 hash
        scanner_md5 = DuplicateScanner(hash_algorithm="md5")
        hash_result_md5 = scanner_md5._calculate_file_hash(test_file)
        assert len(hash_result_md5) == 32  # MD5 hex digest length
    
    def test_files_are_identical(self):
        """Test byte-by-byte file comparison."""
        # Create two identical files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "This is test content for file comparison"
        file1.write_text(content)
        file2.write_text(content)
        
        assert self.scanner._files_are_identical(file1, file2) is True
        
        # Create a different file
        file3 = Path(self.temp_dir) / "file3.txt"
        file3.write_text("Different content")
        
        assert self.scanner._files_are_identical(file1, file3) is False
    
    def test_group_by_size(self):
        """Test grouping files by size."""
        # Create files with different sizes
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        file3 = Path(self.temp_dir) / "file3.txt"
        
        file1.write_text("short")
        file2.write_text("short")
        file3.write_text("longer content")
        
        files = [file1, file2, file3]
        size_groups = self.scanner._group_by_size(files)
        
        # Should have 2 size groups
        assert len(size_groups) == 2
        
        # Check that files are grouped correctly
        sizes = list(size_groups.keys())
        assert len(size_groups[sizes[0]]) == 2  # Two files with same size
        assert len(size_groups[sizes[1]]) == 1  # One file with different size
    
    def test_find_duplicates_hash(self):
        """Test hash-based duplicate detection."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        file3 = Path(self.temp_dir) / "file3.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text("different content")
        
        files = [file1, file2, file3]
        duplicate_groups = self.scanner._find_duplicates_hash(files)
        
        assert len(duplicate_groups) == 1
        assert len(duplicate_groups[0]) == 2
        assert file1 in duplicate_groups[0]
        assert file2 in duplicate_groups[0]
        assert file3 not in duplicate_groups[0]
    
    def test_find_duplicates_byte_comparison(self):
        """Test byte-by-byte duplicate detection."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        file3 = Path(self.temp_dir) / "file3.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text("different content")
        
        files = [file1, file2, file3]
        duplicate_groups = self.scanner._find_duplicates_byte_comparison(files)
        
        assert len(duplicate_groups) == 1
        assert len(duplicate_groups[0]) == 2
        assert file1 in duplicate_groups[0]
        assert file2 in duplicate_groups[0]
        assert file3 not in duplicate_groups[0]
    
    def test_scan_no_duplicates(self):
        """Test scanning when no duplicates exist."""
        # Create unique files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        file1.write_text("content 1")
        file2.write_text("content 2")
        
        paths = [Path(self.temp_dir)]
        duplicate_groups = self.scanner.scan(paths)
        
        assert len(duplicate_groups) == 0
    
    def test_scan_with_duplicates(self):
        """Test scanning with duplicates."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        paths = [Path(self.temp_dir)]
        duplicate_groups = self.scanner.scan(paths)
        
        assert len(duplicate_groups) == 1
        assert len(duplicate_groups[0]) == 2
    
    def test_scan_with_byte_comparison(self):
        """Test scanning with byte-by-byte comparison."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        paths = [Path(self.temp_dir)]
        duplicate_groups = self.scanner.scan(paths, use_byte_comparison=True)
        
        assert len(duplicate_groups) == 1
        assert len(duplicate_groups[0]) == 2
    
    def test_output_results(self, capsys):
        """Test results output formatting."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        duplicate_groups = [[file1, file2]]
        self.scanner.output_results(duplicate_groups)
        
        captured = capsys.readouterr()
        assert "Found 1 duplicate groups" in captured.out
        assert "1 duplicate files" in captured.out
        assert "[KEEP]" in captured.out
        assert "[DUPLICATE]" in captured.out
    
    def test_purge_duplicates_dry_run(self):
        """Test dry run mode for purging duplicates."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        duplicate_groups = [[file1, file2]]
        
        # Dry run should not delete files
        removed_count = self.scanner.purge_duplicates(duplicate_groups, dry_run=True)
        
        assert removed_count == 0
        assert file1.exists()
        assert file2.exists()
    
    def test_purge_duplicates_actual(self):
        """Test actual purging of duplicates."""
        # Create duplicate files
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        duplicate_groups = [[file1, file2]]
        
        # Actual purge should delete duplicate files
        removed_count = self.scanner.purge_duplicates(duplicate_groups, dry_run=False)
        
        assert removed_count == 1
        assert file1.exists()  # First file should be kept
        assert not file2.exists()  # Second file should be deleted
    
    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        paths = [Path(self.temp_dir)]
        duplicate_groups = self.scanner.scan(paths)
        
        assert len(duplicate_groups) == 0
    
    def test_scan_nonexistent_path(self):
        """Test scanning a non-existent path."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent"
        paths = [nonexistent_path]
        
        # Should handle gracefully and return empty result
        duplicate_groups = self.scanner.scan(paths)
        assert len(duplicate_groups) == 0
    
    def test_scan_with_size_filtering(self):
        """Test scanning with size filtering."""
        # Create files with different sizes
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        
        file1.write_text("short")
        file2.write_text("much longer content for testing")
        
        # Test min_size filtering
        scanner = DuplicateScanner(min_size=20)
        paths = [Path(self.temp_dir)]
        duplicate_groups = scanner.scan(paths)
        
        # Should only consider file2 (larger than 20 bytes)
        assert len(duplicate_groups) == 0  # No duplicates
        
        # Test max_size filtering
        scanner = DuplicateScanner(max_size=10)
        duplicate_groups = scanner.scan(paths)
        
        # Should only consider file1 (smaller than 10 bytes)
        assert len(duplicate_groups) == 0  # No duplicates


class TestUtils:
    """Test utility functions."""
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"
        
        # Test precision
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(15360) == "15.0 KB" 