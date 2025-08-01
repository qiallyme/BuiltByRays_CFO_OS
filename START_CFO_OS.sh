#!/bin/bash

# BuiltByRays™ CFO OS - Automatic Startup Script
# For Unix/Linux systems

echo
echo "========================================"
echo "🏢 BuiltByRays™ CFO OS"
echo "========================================"
echo "🚀 Starting automatically..."
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

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_status "Python 3 found" "success"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_status "Python found" "success"
else
    print_status "Python not found!" "error"
    echo
    echo "Please install Python 3.8 or higher:"
    echo "• Ubuntu/Debian: sudo apt install python3"
    echo "• macOS: brew install python3"
    echo "• Or download from: https://python.org/downloads/"
    echo
    echo "After installing Python, run this script again."
    echo
    exit 1
fi

# Check if Node.js is installed (optional)
if command -v node &> /dev/null; then
    print_status "Node.js found" "success"
else
    print_status "Node.js not found - Electron app will be skipped" "warning"
    echo "You can install Node.js from: https://nodejs.org/"
    echo
fi

echo
print_status "Starting BuiltByRays™ CFO OS..." "info"
echo

# Run the automatic startup script
$PYTHON_CMD auto_start.py

echo
echo "========================================"
print_status "BuiltByRays™ CFO OS has started!" "success"
echo "========================================"
echo
echo "📱 Your application is now running at:"
echo "   • Web Interface: http://localhost:5000"
echo "   • Desktop App: Check for Electron window"
echo
echo "⚠️  Don't forget to add your OpenAI API key to the .env file"
echo 