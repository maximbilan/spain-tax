#!/bin/bash

# Spanish IRPF Tax Calculator - Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the calculator

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Spanish IRPF Tax Calculator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python 3 is available
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check Python version (need 3.7+)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}Python version: $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --quiet --upgrade pip

# Install dependencies (if any)
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --quiet -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}Dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""

# Run the calculator
# If arguments are provided, pass them to the script
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage: $0 <income> [options]${NC}"
    echo -e "${YELLOW}Example: $0 60000 --verbose${NC}"
    echo ""
    echo -e "${BLUE}Running with example income of €60,000...${NC}"
    echo ""
    $PYTHON_CMD "$SCRIPT_DIR/irpf_calculator.py" 60000 --verbose
else
    $PYTHON_CMD "$SCRIPT_DIR/irpf_calculator.py" "$@"
fi
