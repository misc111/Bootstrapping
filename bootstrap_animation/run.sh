#!/bin/bash
# Quick start script for Bootstrap Animation

echo "========================================"
echo " Bootstrap Animation - Starting..."
echo "========================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for virtual environment in parent directory or local
if [ -d "../.venv" ]; then
    VENV_PATH="../.venv"
    echo "Using virtual environment: ../venv"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
    echo "Using virtual environment: venv"
else
    echo "⚠️  No virtual environment found!"
    echo ""
    echo "Please create one first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"
echo "✓ Virtual environment activated"
echo ""

# Check if dependencies are installed
if ! python -c "import chainladder, dash, plotly" 2>/dev/null; then
    echo "Installing dependencies..."
    python -m pip install -q --upgrade pip
    python -m pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
    echo ""
fi

# Run the application
echo "Starting Dash application..."
echo "Open your browser to: http://127.0.0.1:8050"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

python app.py
