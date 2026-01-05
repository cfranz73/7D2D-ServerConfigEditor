#!/bin/bash
# Build script for 7D2D Server Config Editor
# This creates a standalone Windows executable with all resources bundled

echo "========================================"
echo "Building 7D2D Server Config Editor"
echo "========================================"
echo

# Clean previous build
if [ -f "dist/7D2D-ServerConfigEditor.exe" ]; then
    echo "Cleaning previous build..."
    rm -f "dist/7D2D-ServerConfigEditor.exe"
fi

# Run PyInstaller
echo
echo "Running PyInstaller..."
python -m PyInstaller --onefile --windowed \
    --name "7D2D-ServerConfigEditor" \
    --icon="icon.ico" \
    --add-data "icon.ico:." \
    --add-data "Logos and Images:Logos and Images" \
    7d2d_server_config_editor.py

# Check if build succeeded
if [ -f "dist/7D2D-ServerConfigEditor.exe" ]; then
    echo
    echo "========================================"
    echo "Build completed successfully!"
    echo "========================================"
    echo
    echo "Executable location: dist/7D2D-ServerConfigEditor.exe"
    echo "File size:"
    ls -lh "dist/7D2D-ServerConfigEditor.exe"
    echo
else
    echo
    echo "========================================"
    echo "Build FAILED!"
    echo "========================================"
    echo
    echo "Check the error messages above."
    exit 1
fi
