#!/usr/bin/env python3
"""
BuiltByRAVE CFO OS Setup Script
Automated installation and setup for the complete CFO OS package
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🏢 BuiltByRAVE™ CFO OS - Complete Setup")
    print("=" * 60)
    print("Automated installation and configuration")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_python_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python requirements...")
    try:
        requirements_file = Path("rag-backend/requirements.txt")
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python requirements: {e}")
        return False

def install_node_dependencies():
    """Install Node.js dependencies for Electron app"""
    print("\n📦 Installing Node.js dependencies...")
    try:
        electron_dir = Path("electron-app")
        if not electron_dir.exists():
            print("❌ electron-app directory not found")
            return False
        
        # Check if npm is available
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=electron_dir, check=True)
        print("✅ Node.js dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  npm not found. Please install Node.js first")
        return False

def create_env_file():
    """Create .env file template"""
    print("\n🔧 Creating environment configuration...")
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# BuiltByRAVE CFO OS Configuration
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize server settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("   Please add your OpenAI API key to the .env file")
    else:
        print("✅ .env file already exists")

def check_vault_structure():
    """Check if vault directory structure is correct"""
    print("\n📁 Checking vault structure...")
    vault_path = Path("vault")
    if not vault_path.exists():
        print("❌ Vault directory not found")
        return False
    
    # Check for essential directories
    essential_dirs = ["00-Home", "01-Scope", "09-Financials"]
    missing_dirs = []
    
    for dir_name in essential_dirs:
        if not (vault_path / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"⚠️  Missing essential vault directories: {', '.join(missing_dirs)}")
    else:
        print("✅ Vault structure looks good")
    
    return True

def create_startup_scripts():
    """Create platform-specific startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting BuiltByRAVE CFO OS...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Start the chatbot
cd rag-backend
python chatbot.py
pause
"""
        with open("start_cfo_os.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created start_cfo_os.bat")
    
    # Unix shell script
    shell_content = """#!/bin/bash

echo "Starting BuiltByRAVE CFO OS..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Start the chatbot
cd rag-backend
python3 chatbot.py
"""
    with open("start_cfo_os.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("start_cfo_os.sh", 0o755)
    
    print("✅ Created start_cfo_os.sh")

def run_tests():
    """Run basic tests to ensure everything works"""
    print("\n🧪 Running basic tests...")
    
    # Test Python imports
    try:
        import flask
        import openai
        import chromadb
        print("✅ Python dependencies test passed")
    except ImportError as e:
        print(f"❌ Python dependency test failed: {e}")
        return False
    
    # Test vault loading
    try:
        from rag_backend.loader import load_documents
        docs = load_documents("vault")
        print(f"✅ Vault loading test passed ({len(docs)} documents)")
    except Exception as e:
        print(f"⚠️  Vault loading test failed: {e}")
    
    return True

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_python_requirements():
        return False
    
    if not install_node_dependencies():
        print("⚠️  Node.js dependencies failed, but continuing...")
    
    # Setup configuration
    create_env_file()
    
    # Check structure
    check_vault_structure()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Run start_cfo_os.bat (Windows) or ./start_cfo_os.sh (Unix)")
    print("3. Open http://localhost:5000 in your browser")
    print("\nFor Electron app:")
    print("1. cd electron-app")
    print("2. npm start")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 