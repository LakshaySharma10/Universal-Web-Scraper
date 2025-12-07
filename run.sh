#!/bin/bash

# Lyftr AI - Full-stack Assignment
# Universal Website Scraper (MVP) + JSON Viewer

set -e

echo "Setting up project..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment using uv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

# Install Python dependencies
echo "Installing Python dependencies..."
uv pip install -r requirements.txt

# Install Playwright browsers if needed
echo "Installing Playwright browsers..."
python -m playwright install chromium || echo "Playwright browsers already installed or installation skipped"

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Start the server
echo "Starting server on http://localhost:8000..."
echo ""
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

