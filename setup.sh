#!/bin/bash

# API Monitor System - Setup Script
# This script helps you set up the development environment

set -e

echo "========================================="
echo "  API Monitor System - Setup Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Running from project root"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python 3 found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✓${NC} Docker found"
else
    echo -e "${YELLOW}⚠${NC}  Docker not found (optional, required for containerized deployment)"
fi

# Check Docker Compose
if command_exists docker-compose; then
    echo -e "${GREEN}✓${NC} Docker Compose found"
else
    echo -e "${YELLOW}⚠${NC}  Docker Compose not found (optional, required for containerized deployment)"
fi

# Setup Backend
echo ""
echo "========================================="
echo "  Backend Setup"
echo "========================================="

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC}  Please edit backend/.env with your credentials"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Create necessary directories
mkdir -p secrets database
echo -e "${GREEN}✓${NC} Created secrets and database directories"

# Deactivate venv
deactivate

cd ..

# Setup Frontend
echo ""
echo "========================================="
echo "  Frontend Setup"
echo "========================================="

cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓${NC} Node.js dependencies installed"
else
    echo -e "${GREEN}✓${NC} Node.js dependencies already installed"
fi

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
EOF
    echo -e "${YELLOW}⚠${NC}  Please edit frontend/.env with your Firebase config"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

cd ..

# Setup Infrastructure
echo ""
echo "========================================="
echo "  Infrastructure Setup"
echo "========================================="

cd infrastructure

# Create .env for docker-compose
if [ ! -f ".env" ]; then
    echo "Creating infrastructure .env file..."
    cp ../backend/.env.example .env
    echo -e "${YELLOW}⚠${NC}  Please edit infrastructure/.env with your credentials"
else
    echo -e "${GREEN}✓${NC} Infrastructure .env file already exists"
fi

cd ..

# Summary
echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure Firebase:"
echo "   - Create Firebase project at https://console.firebase.google.com"
echo "   - Enable Authentication and Firestore"
echo "   - Download Admin SDK key to backend/secrets/firebase-credentials.json"
echo "   - Update backend/.env with Firebase project ID"
echo "   - Update frontend/.env with Firebase config"
echo ""
echo "2. Get Google Cloud credentials:"
echo "   - Get Gemini API key from https://makersuite.google.com/app/apikey"
echo "   - Update backend/.env with Gemini API key"
echo ""
echo "3. Run the application:"
echo ""
echo "   Option A - Local Development:"
echo "   Terminal 1: cd backend && source venv/bin/activate && python main.py"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "   Option B - Docker Compose:"
echo "   cd infrastructure && docker-compose up -d"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "For full deployment instructions, see docs/DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${GREEN}Setup completed successfully!${NC}"
