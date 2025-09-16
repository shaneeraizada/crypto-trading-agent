# ============================================================================
# scripts/setup/setup.sh
# ============================================================================
#!/bin/bash

# Crypto Trading Agent Setup Script

set -e  # Exit on any error

echo "🚀 Setting up Crypto Trading Agent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD=python3.11
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        if (( $(echo "$PYTHON_VERSION >= 3.11" | bc -l) )); then
            PYTHON_CMD=python3
        else
            print_error "Python 3.11+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3.11+ is not installed"
        exit 1
    fi
    print_status "Python check passed: $($PYTHON_CMD --version)"
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Environment file created from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs/trading
    mkdir -p logs/data
    mkdir -p logs/errors
    mkdir -p data/raw
    mkdir -p data/processed
    mkdir -p data/models
    mkdir -p data/backups
    print_status "Directories created"
}

# Setup database (if Docker is available)
setup_database() {
    print_status "Checking for Docker..."
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_status "Docker found. Starting database services..."
        docker-compose up -d db redis
        sleep 10  # Wait for services to start
        
        print_status "Initializing database..."
        $PYTHON_CMD scripts/setup/init_database.py
        print_status "Database setup complete"
    else
        print_warning "Docker not found. Please setup PostgreSQL and Redis manually"
        print_warning "Then run: python scripts/setup/init_database.py"
    fi
}

# Setup pre-commit hooks
setup_hooks() {
    print_status "Setting up pre-commit hooks..."
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_status "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found. Skipping hook setup"
    fi
}

# Run setup steps
main() {
    echo "🔧 Crypto Trading Agent Setup"
    echo "============================="
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_env
    create_directories
    setup_database
    setup_hooks
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run: source venv/bin/activate"
    echo "3. Run: uvicorn src.api.app:app --reload"
    echo ""
    echo "Access the API at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
}

# Run main function
main