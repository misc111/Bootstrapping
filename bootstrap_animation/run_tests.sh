#!/bin/bash
# Run comprehensive tests for Bootstrap Animation

echo "========================================"
echo " Running Comprehensive Test Suite"
echo "========================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for virtual environment in parent directory or local
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✓ Virtual environment activated: ../.venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated: venv"
else
    echo "⚠️  No virtual environment found"
    echo "   Tests will use system Python"
fi

echo ""

# Run tests
python test_comprehensive.py

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed - application is ready to run!"
    echo ""
    echo "To start the application:"
    echo "  python3 app.py"
else
    echo "✗ Some tests failed - please review the errors above"
    echo ""
    echo "Common fixes:"
    echo "  1. Install missing dependencies: pip install -r requirements.txt"
    echo "  2. Check that all .py files are in the current directory"
    echo "  3. Verify Python version is 3.8 or higher"
fi

echo ""

exit $TEST_EXIT_CODE
