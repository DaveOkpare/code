#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Setting up the Tool-Calling RL Environment..."

# 1. Install Python dependencies
if [ -f "pyproject.toml" ]; then
    echo "Installing dependencies from pyproject.toml..."
    pip install .
else
    echo "Installing core dependencies..."
    pip install gymnasium langchain pydantic docker pytest streamlit
fi

# 2. Check for Docker
if command -v docker &> /dev/null; then
    echo "Docker is installed. You can use 'docker build' for containerized runs."
else
    echo "Warning: Docker not found. Containerized features will not be available."
fi

# 3. Create necessary directories
mkdir -p data/scenarios
mkdir -p logs
mkdir -p tests

# 4. Print helpful information
echo "--------------------------------------------------"
echo "Setup Complete!"
echo "To run the environment locally: python main.py"
echo "To run tests: pytest"
echo "To start the dashboard (once implemented): streamlit run app.py"
echo "--------------------------------------------------"
