#!/bin/bash
# Lorex Camera Dashboard - Linux/macOS Launcher
echo "============================================================"
echo "  Lorex Camera Dashboard"
echo "============================================================"
echo ""

# Find python
PYTHON=""
for cmd in python3 python; do
    if command -v $cmd &>/dev/null; then
        PYTHON=$cmd
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found! Please install Python 3."
    exit 1
fi

echo "Installing required package (requests)..."
$PYTHON -m pip install requests -q

echo "Starting dashboard..."
$PYTHON "$(dirname "$0")"/dashboard.py
