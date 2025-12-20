#!/bin/bash
# Script to publish nexus-client to PyPI

set -e

echo "=========================================="
echo "Publishing nexus-client to PyPI"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Run this from the nexus-python directory."
    exit 1
fi

# Check if build tools are installed
if ! python3 -m pip show build twine > /dev/null 2>&1; then
    echo "Installing build tools..."
    python3 -m pip install --upgrade build twine
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info 2>/dev/null || true

# Build the package
echo ""
echo "Building package..."
python3 -m build

# Check what was built
echo ""
echo "Build artifacts:"
ls -lh dist/

# Ask for confirmation
echo ""
echo "=========================================="
echo "Ready to publish!"
echo "=========================================="
echo ""
echo "Built files:"
ls -1 dist/
echo ""
read -p "Do you want to publish to PyPI? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Publishing cancelled."
    exit 0
fi

# Check for PyPI credentials
if [ -z "$TWINE_USERNAME" ] && [ -z "$PYPI_USERNAME" ]; then
    echo ""
    echo "Note: You'll need PyPI credentials."
    echo "Set environment variables:"
    echo "  export TWINE_USERNAME=your_username"
    echo "  export TWINE_PASSWORD=your_password"
    echo ""
    echo "Or use API tokens:"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-your-api-token"
    echo ""
    read -p "Continue with interactive authentication? (yes/no): " use_interactive
    if [ "$use_interactive" != "yes" ]; then
        echo "Publishing cancelled. Set credentials and try again."
        exit 0
    fi
fi

# Publish to PyPI
echo ""
echo "Publishing to PyPI..."
python3 -m twine upload dist/*

echo ""
echo "=========================================="
echo "✅ Published successfully!"
echo "=========================================="
echo ""
echo "Package should be available at:"
echo "  https://pypi.org/project/nexus-client/"
echo ""
echo "Install with:"
echo "  pip install nexus-client"
echo "  pip install nexus-client[langgraph]"

