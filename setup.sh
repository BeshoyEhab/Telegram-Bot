# =============================================================================
# FILE: setup.sh
# DESCRIPTION: Automated setup script for Linux/Mac
# LOCATION: Project root directory
# PURPOSE: Automates installation, venv creation, database setup
# USAGE: chmod +x setup.sh && ./setup.sh
# =============================================================================

#!/bin/bash

# Telegram School Bot - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=========================================="
echo "Telegram School Bot - Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo -e "${RED}Error: Python 3.9 or higher is required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env file and add your BOT_API token${NC}"
    echo -e "${YELLOW}⚠ Also add your Telegram user ID to USERS variable${NC}"
    echo ""
    echo "Press Enter after you've edited the .env file..."
    read
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs backups exports templates database/migrations/versions
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Initialize database
echo "Initializing database..."
python -c "from database import init_db; init_db()"
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Create initial migration
echo "Creating initial migration..."
if [ ! "$(ls -A database/migrations/versions/)" ]; then
    alembic revision --autogenerate -m "Initial migration"
    echo -e "${GREEN}✓ Initial migration created${NC}"
else
    echo -e "${YELLOW}Migrations already exist${NC}"
fi
echo ""

# Apply migrations
echo "Applying migrations..."
alembic upgrade head
echo -e "${GREEN}✓ Migrations applied${NC}"
echo ""

# Test database connection
echo "Testing database connection..."
if python -c "from database import check_connection; exit(0 if check_connection() else 1)"; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    exit 1
fi
echo ""

# Test configuration
echo "Testing configuration..."
if python -c "import config; print(f'Bot Token: {config.BOT_API[:10]}...'); print(f'Authorized Users: {len(config.AUTHORIZED_USERS)}')"; then
    echo -e "${GREEN}✓ Configuration loaded successfully${NC}"
else
    echo -e "${RED}✗ Configuration failed${NC}"
    exit 1
fi
echo ""

# Run tests
echo "Running basic tests..."
if python -m pytest tests/test_config.py -v; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed (this is OK for initial setup)${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure you've added your BOT_API token to .env"
echo "2. Add your Telegram ID to USERS in .env"
echo "3. Run the bot: python main.py"
echo ""
echo "To activate the virtual environment later, run:"
echo "  source venv/bin/activate"
echo ""
