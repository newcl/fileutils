#!/bin/bash

echo "Setting up deduper CLI tool..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or later"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Installing deduper..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "Error: Failed to install deduper"
    exit 1
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "To use deduper:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run deduper: deduper scan /path/to/directory"
echo
echo "Or use the launcher script: ./deduper.sh scan /path/to/directory"
echo 