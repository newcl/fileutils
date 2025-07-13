"""
Utility functions for the deduper package.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate log messages
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(name)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB", "2.3 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    # Define size units
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    # Calculate the appropriate unit
    import math
    unit_index = int(math.floor(math.log(size_bytes, 1024)))
    unit_index = min(unit_index, len(units) - 1)
    
    # Convert to the appropriate unit
    size_in_unit = size_bytes / (1024 ** unit_index)
    
    # Format with appropriate precision
    if unit_index == 0:  # Bytes
        return f"{size_in_unit:.0f} {units[unit_index]}"
    elif size_in_unit < 10:
        return f"{size_in_unit:.2f} {units[unit_index]}"
    elif size_in_unit < 100:
        return f"{size_in_unit:.1f} {units[unit_index]}"
    else:
        return f"{size_in_unit:.0f} {units[unit_index]}"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform.startswith('win')


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform.startswith('darwin')


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith('linux')


def get_platform_info() -> str:
    """Get platform information."""
    import platform
    
    system = platform.system()
    release = platform.release()
    version = platform.version()
    
    return f"{system} {release} ({version})"


def safe_filename(filename: str) -> str:
    """
    Convert a filename to a safe version that works across platforms.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename with problematic characters replaced
    """
    import re
    
    # Replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    # Limit length (Windows has 255 character limit for full path)
    if len(safe_name) > 200:
        name, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
        safe_name = name[:200-len(ext)-1] + ('.' + ext if ext else '')
    
    return safe_name


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (including the dot) or empty string if no extension
    """
    import os
    _, ext = os.path.splitext(file_path)
    return ext.lower()


def is_binary_file(file_path: str, sample_size: int = 1024) -> bool:
    """
    Check if a file is binary by examining its content.
    
    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample from the beginning of the file
        
    Returns:
        True if the file appears to be binary, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
            
        # Check for null bytes (common in binary files)
        if b'\x00' in sample:
            return True
        
        # Check if the sample contains mostly printable ASCII
        try:
            sample.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
            
    except (OSError, IOError):
        # If we can't read the file, assume it's not binary
        return False


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    import os
    import time
    from pathlib import Path
    
    path = Path(file_path)
    
    try:
        stat = path.stat()
        
        info = {
            'name': path.name,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': time.ctime(stat.st_ctime),
            'modified': time.ctime(stat.st_mtime),
            'accessed': time.ctime(stat.st_atime),
            'extension': get_file_extension(file_path),
            'is_binary': is_binary_file(file_path),
            'is_symlink': path.is_symlink(),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
        }
        
        return info
        
    except (OSError, IOError) as e:
        return {
            'name': path.name,
            'error': str(e)
        } 