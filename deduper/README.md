# Deduper CLI

A command-line tool to find and manage duplicate files in directories.

## Installation

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e .
```

## Usage

### Scan for duplicates
```bash
deduper scan <folder_path>
```

### Delete duplicates (keep only one copy)
```bash
deduper scan <folder_path> --delete
```

## How it works

The tool uses a two-step process to ensure 100% accuracy:

1. **Hash-based grouping**: Files are first grouped by their SHA-256 hash for fast initial comparison
2. **Byte-by-byte verification**: Files with the same hash are then compared byte-by-byte to eliminate any potential hash collisions and ensure they are truly identical

This approach provides the speed of hash-based comparison while guaranteeing no false positives through byte-by-byte verification.

## Deletion behavior

When using the `--delete` option, the tool will:
- Keep the file with the **shortest filename** in each duplicate group
- If multiple files have the same filename length, keep the first one encountered
- Delete all other duplicate files in the group

## Options

- `--delete`: Delete duplicate files, keeping only one copy (default: only print duplicates) 