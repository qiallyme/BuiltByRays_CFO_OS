#!/usr/bin/env python3
"""
CFO AI Chatbot Startup Script
BuiltByRays™ CFO OS
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "rag-backend/requirements.txt"
        ], check=True)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_vault_exists():
    """Check if vault directory exists"""
    vault_path = Path("vault")
    if not vault_path.exists():
        print("❌ Vault directory not found")
        return False
    print("✅ Vault directory found")
    return True

def start_chatbot():
    """Start the chatbot backend"""
    print("🚀 Starting CFO AI Chatbot...")
    
    # Change to rag-backend directory
    os.chdir("rag-backend")
    
    try:
        # Start the Flask app
        subprocess.run([
            sys.executable, "chatbot.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Chatbot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start chatbot: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main startup function"""
    print("=" * 50)
    print("🏢 BuiltByRays™ CFO OS - AI Chatbot")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_vault_exists():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎯 Starting chatbot...")
    print("📱 Chat interface will be available at: http://localhost:5000")
    print("💬 Web chat interface: http://localhost:5000/chat")
    print("📊 Health check: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the chatbot")
    print("-" * 50)
    
    # Start the chatbot
    start_chatbot()

if __name__ == "__main__":
    main() 