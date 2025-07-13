# Deduper

A platform-agnostic CLI tool for finding and managing duplicate files with high accuracy and multiple detection methods.

## Features

- **Multiple Detection Methods**: Hash-based comparison (fast) or byte-by-byte comparison (most accurate)
- **Platform Agnostic**: Works on Windows, macOS, and Linux
- **Flexible Scanning**: Scan single files, directories, or multiple paths
- **Smart Filtering**: Filter by file size, follow symlinks, recursive scanning
- **Safe Operations**: Dry-run mode to preview changes before deletion
- **Comprehensive Output**: Detailed reports with space savings calculations
- **No Dependencies**: Uses only Python standard library

## Installation

### Option 1: Virtual Environment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd deduper

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Option 2: Direct Installation

```bash
# Install directly from the source directory
pip install -e .
```

### Option 3: Direct Usage (No Installation)

```bash
# Run directly without installation
python -m deduper scan /path/to/directory

# Or use the standalone script
python deduper.py scan /path/to/directory
```

### Option 4: Using Launcher Scripts

```bash
# Windows (using batch file)
deduper.bat scan /path/to/directory

# Unix/Linux (using shell script)
chmod +x deduper.sh
./deduper.sh scan /path/to/directory
```

## Usage

After installation, you can use `deduper` directly as a command:

### Basic Scanning

```bash
# Scan a directory for duplicates using hash comparison
deduper scan /path/to/directory

# Scan multiple directories
deduper scan /path1 /path2 /path3

# Scan with verbose output
deduper scan /path/to/directory --verbose
```

### If the `deduper` command is not found:

If you installed in a virtual environment, make sure it's activated. Otherwise, use one of these alternatives:

```bash
# Using Python module
python -m deduper scan /path/to/directory

# Using standalone script
python deduper.py scan /path/to/directory

# Using launcher scripts
deduper.bat scan /path/to/directory  # Windows
./deduper.sh scan /path/to/directory  # Unix/Linux
```

### High Accuracy Mode

```bash
# Use byte-by-byte comparison for maximum accuracy
deduper scan /path/to/directory --all-bytes
```

### File Size Filtering

```bash
# Only consider files larger than 1MB
deduper scan /path/to/directory --min-size 1048576

# Only consider files smaller than 100MB
deduper scan /path/to/directory --max-size 104857600
```

### Removing Duplicates

```bash
# Preview what would be removed (dry run)
deduper scan /path/to/directory --purge --dry-run

# Actually remove duplicate files (keep one copy)
deduper scan /path/to/directory --purge
```

### Output Options

```bash
# Save results to a file
deduper scan /path/to/directory --output results.txt

# Use different hash algorithm
deduper scan /path/to/directory --hash-algorithm sha512
```

### Advanced Options

```bash
# Follow symbolic links
deduper scan /path/to/directory --follow-symlinks

# Non-recursive scanning (only direct children)
deduper scan /path/to/directory --no-recursive

# Quiet mode (suppress all output except errors)
deduper scan /path/to/directory --quiet
```

## Command Line Options

### Global Options

- `--version`: Show version and exit
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress all output except errors

### Scan Command Options

- `paths`: One or more directories or files to scan
- `--all-bytes`: Use byte-by-byte comparison instead of hash
- `--purge`: Remove duplicate files, keeping only one copy
- `--output, -o`: Output file to save results
- `--hash-algorithm`: Hash algorithm to use (md5, sha1, sha256, sha512)
- `--min-size`: Minimum file size in bytes to consider
- `--max-size`: Maximum file size in bytes to consider
- `--recursive, -r`: Scan directories recursively (default: True)
- `--follow-symlinks`: Follow symbolic links
- `--dry-run`: Show what would be done without actually doing it

## Output Format

The tool provides detailed output showing:

- Number of duplicate groups found
- Total number of duplicate files
- Space that could be saved
- For each group:
  - Number of files and individual file size
  - Space wasted by duplicates
  - List of files with [KEEP] and [DUPLICATE] markers

Example output:
```
Found 3 duplicate groups with 5 duplicate files.
Total space that could be saved: 15.2 MB

Group 1 (3 files, 5.1 MB each):
  Space wasted: 10.2 MB
  1. /path/file1.txt [KEEP]
  2. /path/file1_copy.txt [DUPLICATE]
  3. /path/file1_backup.txt [DUPLICATE]

Group 2 (2 files, 2.5 MB each):
  Space wasted: 2.5 MB
  1. /path/image.jpg [KEEP]
  2. /path/image_copy.jpg [DUPLICATE]
```

## Detection Methods

### Hash-Based Comparison (Default)
- Uses cryptographic hash functions (SHA-256 by default)
- Fast and efficient for large files
- Extremely low probability of false positives
- Supports MD5, SHA-1, SHA-256, and SHA-512

### Byte-by-Byte Comparison
- Reads and compares files byte by byte
- Maximum accuracy - guaranteed to find exact duplicates
- Slower than hash-based method
- Useful when absolute certainty is required

## Platform Support

The tool is designed to work across all major platforms:

- **Windows**: Full support for NTFS and FAT filesystems
- **macOS**: Support for HFS+ and APFS filesystems
- **Linux**: Support for all major filesystems (ext4, btrfs, etc.)

## Safety Features

- **Dry Run Mode**: Preview all operations before execution
- **Permission Handling**: Graceful handling of permission errors
- **Error Recovery**: Continues scanning even if individual files fail
- **Safe Deletion**: Only removes files identified as duplicates

## Performance Considerations

- **Hash Method**: Best for large directories and files
- **Byte-by-Byte**: Best for small files or when maximum accuracy is needed
- **Memory Usage**: Processes files in chunks to minimize memory usage
- **Progress Feedback**: Verbose mode shows scanning progress

## Examples

### Find duplicates in Downloads folder
```bash
deduper scan ~/Downloads
```

### Remove duplicates from multiple photo directories
```bash
deduper scan ~/Pictures ~/Photos --purge --all-bytes
```

### Find large duplicate files only
```bash
deduper scan /path/to/directory --min-size 10485760 --output large_duplicates.txt
```

### Preview what would be removed
```bash
deduper scan /path/to/directory --purge --dry-run --verbose
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 