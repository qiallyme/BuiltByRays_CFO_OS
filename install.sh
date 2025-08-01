#!/bin/bash

echo "========================================"
echo "BuiltByRAVE CFO OS - Unix/Linux Installer"
echo "========================================"
echo

# Function to print colored output
print_status() {
    case $2 in
        "success") echo -e "\033[32m✅ $1\033[0m" ;;
        "error") echo -e "\033[31m❌ $1\033[0m" ;;
        "warning") echo -e "\033[33m⚠️  $1\033[0m" ;;
        "info") echo -e "\033[34m📋 $1\033[0m" ;;
        *) echo "$1" ;;
    esac
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_status "Running with root privileges" "success"
else
    print_status "Not running as root - some features may be limited" "warning"
fi

echo
print_status "Checking prerequisites..." "info"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION found" "success"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION found" "success"
    PYTHON_CMD="python"
else
    print_status "Python not found. Please install Python 3.8+ from https://python.org" "error"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found" "success"
else
    print_status "Node.js not found. Please install Node.js 16+ from https://nodejs.org" "error"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_status "npm $NPM_VERSION found" "success"
else
    print_status "npm not found. Please install npm" "error"
    exit 1
fi

echo
print_status "Starting installation..." "info"

# Install Python requirements
print_status "Installing Python requirements..." "info"
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r rag-backend/requirements.txt

if [ $? -eq 0 ]; then
    print_status "Python requirements installed" "success"
else
    print_status "Failed to install Python requirements" "error"
    exit 1
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..." "info"
cd electron-app
npm install
if [ $? -eq 0 ]; then
    print_status "Node.js dependencies installed" "success"
else
    print_status "Failed to install Node.js dependencies" "error"
    exit 1
fi
cd ..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..." "info"
    cat > .env << EOF
# BuiltByRAVE CFO OS Configuration
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
EOF
    print_status ".env file created" "success"
    print_status "Please add your OpenAI API key to the .env file" "warning"
else
    print_status ".env file already exists" "success"
fi

# Make startup script executable
chmod +x start_cfo_os.sh

# Create desktop shortcut (Linux)
if command -v xdg-desktop-menu &> /dev/null; then
    print_status "Creating desktop shortcut..." "info"
    cat > BuiltByRAVE-CFO-OS.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BuiltByRAVE CFO OS
Comment=Financial Operating System with AI Chatbot
Exec=$(pwd)/start_cfo_os.sh
Icon=$(pwd)/electron-app/assets/logo.png
Terminal=true
Categories=Office;Finance;
EOF
    xdg-desktop-menu install BuiltByRAVE-CFO-OS.desktop
    rm BuiltByRAVE-CFO-OS.desktop
    print_status "Desktop shortcut created" "success"
fi

echo
echo "========================================"
print_status "Installation completed successfully!" "success"
echo "========================================"
echo
echo "Next steps:"
echo "1. Add your OpenAI API key to the .env file"
echo "2. Run ./start_cfo_os.sh to start the application"
echo "3. Or run 'cd electron-app && npm start' for the desktop app"
echo
echo "For support: support@builtbyrave.com"
echo "========================================" 