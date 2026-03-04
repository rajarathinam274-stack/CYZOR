#!/bin/bash

# 🛒 GROCERY PRICE COMPARATOR - QUICK START SCRIPT
# This script sets up and runs the entire application in one command

set -e  # Exit on error

echo "🛒 ========================================="
echo "   GROCERY PRICE COMPARATOR - QUICK START"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

if [[ ! "$PYTHON_VERSION" > "3.11" ]]; then
    echo "   ⚠️  WARNING: Python 3.11+ recommended"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"

# Create data directory if missing
echo ""
echo "📂 Checking data files..."
if [ ! -d "data" ]; then
    echo "   Creating data directory..."
    mkdir -p data
fi

if [ ! -f "data/stores.csv" ]; then
    echo "   ⚠️  Data files missing. They will be created on first API call."
fi

echo "   ✅ Data directory ready"

# Show next steps
echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "🚀 TO START THE APPLICATION:"
echo ""
echo "   Terminal 1 - Start Backend API:"
echo "   $ uvicorn backend.main:app --reload --port 8000"
echo ""
echo "   Terminal 2 - Open Frontend:"
echo "   $ cd frontend && python -m http.server 8001"
echo ""
echo "   Then visit:"
echo "   • Frontend: http://localhost:8001"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "=========================================="
echo ""
echo "📚 View README.md for complete documentation"
echo ""
