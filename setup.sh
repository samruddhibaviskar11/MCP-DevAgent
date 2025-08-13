#!/bin/bash

# 🚀 MCP Agent Setup Script for Office Environments
# Optimized for limited permissions and offline usage

set -e  # Exit on any error

echo "🚀 MCP Agent Setup - Office Environment Edition"
echo "📂 Working Directory: $(pwd)"
echo "🐍 Python Version: $(python3 --version 2>/dev/null || python --version)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

print_info "Using Python command: $PYTHON_CMD"

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    print_status "Virtual environment created in .venv/"
else
    print_status "Virtual environment already exists"
fi

# Step 2: Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate

# Verify activation
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Virtual environment activated: $VIRTUAL_ENV"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Step 3: Upgrade pip to latest version
print_info "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Step 4: Install dependencies with caching
print_info "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    # Install with pip cache for faster subsequent installs
    python -m pip install -r requirements.txt --cache-dir .venv/pip-cache
    print_status "Dependencies installed successfully"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Step 5: Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        print_info "Creating .env file from template..."
        cp env.example .env
        print_status ".env file created from env.example"
        print_warning "Please edit .env file to add your GitHub token and API keys"
    else
        print_warning "No env.example found, skipping .env creation"
    fi
else
    print_status ".env file already exists"
fi

# Step 6: Preload models for offline usage (optional)
read -p "🤖 Do you want to preload AI models for offline usage? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Preloading sentence transformer models..."
    if [ -f "preload_models.py" ]; then
        python preload_models.py
        print_status "Models preloaded for offline usage"
    else
        print_warning "preload_models.py not found, skipping model preload"
    fi
fi

# Step 7: Create quick run script
print_info "Creating quick run script..."
cat > run_app.sh << 'EOF'
#!/bin/bash
# Quick run script for MCP Agent

echo "🚀 Starting MCP Agent..."

# Activate virtual environment
source .venv/bin/activate

# Check if port 8501 is in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8501 is already in use"
    echo "🔄 Killing existing process..."
    pkill -f "streamlit run app.py" || true
    sleep 2
fi

# Start the application
echo "🌐 Starting Streamlit on http://localhost:8501"
python -m streamlit run app.py --server.port=8501 --server.headless=true

echo "👋 Application stopped"
EOF

chmod +x run_app.sh
print_status "Quick run script created: ./run_app.sh"

# Step 8: Display usage instructions
echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your GitHub token (optional but recommended)"
echo "2. Run the application using one of these methods:"
echo "   • Quick start: ./run_app.sh"
echo "   • Manual: source .venv/bin/activate && streamlit run app.py"
echo "   • Windows: .\\start.bat"
echo ""
echo "🌐 Application will be available at: http://localhost:8501"
echo ""
echo "🔧 Troubleshooting:"
echo "• If port 8501 is busy: pkill -f 'streamlit run app.py'"
echo "• For permission issues: chmod +x *.sh"
echo "• For Python issues: check python3 --version"
echo ""
echo "💡 Pro Tips for Office Environment:"
echo "• All dependencies are cached in .venv/pip-cache/"
echo "• Models are cached in ~/.cache/torch/sentence_transformers/"
echo "• No admin rights required - everything runs in user space"
echo "• .env file keeps your secrets safe and local"
echo ""

# Final verification
print_info "Verifying installation..."
python -c "import streamlit; print(f'Streamlit {streamlit.__version__} installed')"
python -c "import git; print('GitPython available')"
python -c "import github; print('PyGithub available')"

print_status "🎯 MCP Agent is ready to use!" 