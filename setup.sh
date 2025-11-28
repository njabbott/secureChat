#!/bin/bash

# Chat Magic Setup Script

echo "========================================"
echo "  Chat Magic Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy language model for PII detection..."
python -m spacy download en_core_web_lg

echo ""
echo "Backend setup complete!"
echo ""

# Setup frontend
echo "Setting up frontend..."
cd ../frontend

# Check if npm is installed
if ! command -v npm &> /dev/null
then
    echo "Warning: npm is not installed. Please install Node.js and npm to set up the frontend."
    echo "Visit: https://nodejs.org/"
else
    echo "Installing frontend dependencies..."
    npm install
    echo ""
    echo "Frontend setup complete!"
fi

cd ..

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python -m app.main"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open http://localhost:4200 in your browser"
echo ""
echo "4. Click 'Start Indexing' to index your Confluence content"
echo ""
echo "Enjoy Chat Magic!"
echo ""
