#!/usr/bin/env python3
"""
BuiltByRays™ CFO OS - Automatic Startup
Handles complete automation of installation, configuration, and startup
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
import platform

class AutoStartup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.processes = []
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("🏢 BuiltByRays™ CFO OS - Automatic Startup")
        print("=" * 60)
        print("🚀 Starting all services automatically...")
        print("=" * 60)
    
    def check_and_install_dependencies(self):
        """Check and install all dependencies automatically"""
        print("📦 Checking and installing dependencies...")
        
        try:
            # Install Python requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.root_dir / "rag-backend" / "requirements.txt")
            ], check=True, capture_output=True)
            print("✅ Python dependencies installed")
            
            # Install Node.js dependencies
            electron_dir = self.root_dir / "electron-app"
            if electron_dir.exists():
                subprocess.run(["npm", "install"], cwd=electron_dir, check=True, capture_output=True)
                print("✅ Node.js dependencies installed")
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Some dependencies failed to install: {e}")
            print("   Continuing anyway...")
        except FileNotFoundError:
            print("⚠️  npm not found, skipping Node.js dependencies")
    
    def setup_environment(self):
        """Setup environment automatically"""
        print("🔧 Setting up environment...")
        
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            env_content = """# BuiltByRays™ CFO OS Configuration
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize server settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
            with open(env_file, "w") as f:
                f.write(env_content)
            print("✅ Created .env file template")
            print("⚠️  Please add your OpenAI API key to the .env file")
        else:
            print("✅ .env file already exists")
    
    def start_vault_watcher(self):
        """Start the vault watcher automatically"""
        print("👁️  Starting vault watcher...")
        
        watcher_path = self.root_dir / "VaultSyncDaemon.exe"
        if watcher_path.exists():
            try:
                if platform.system() == "Windows":
                    subprocess.Popen([str(watcher_path)], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([str(watcher_path)])
                print("✅ Vault watcher started")
            except Exception as e:
                print(f"⚠️  Failed to start vault watcher: {e}")
        else:
            print("⚠️  Vault watcher not found")
    
    def start_python_backend(self):
        """Start the Python backend"""
        print("🐍 Starting Python backend...")
        
        backend_path = self.root_dir / "rag-backend" / "chatbot.py"
        if backend_path.exists():
            try:
                # Start backend in a separate thread
                def run_backend():
                    os.chdir(self.root_dir / "rag-backend")
                    subprocess.run([sys.executable, "chatbot.py"])
                
                backend_thread = threading.Thread(target=run_backend, daemon=True)
                backend_thread.start()
                
                # Wait a moment for the backend to start
                time.sleep(3)
                print("✅ Python backend started")
                return True
            except Exception as e:
                print(f"❌ Failed to start Python backend: {e}")
                return False
        else:
            print("❌ Backend file not found")
            return False
    
    def start_electron_app(self):
        """Start the Electron app"""
        print("⚡ Starting Electron app...")
        
        electron_dir = self.root_dir / "electron-app"
        if electron_dir.exists():
            try:
                subprocess.Popen(["npm", "start"], cwd=electron_dir)
                print("✅ Electron app started")
                return True
            except Exception as e:
                print(f"❌ Failed to start Electron app: {e}")
                return False
        else:
            print("⚠️  Electron app not found")
            return False
    
    def open_web_interface(self):
        """Open the web interface in browser"""
        print("🌐 Opening web interface...")
        
        # Wait a bit for the backend to fully start
        time.sleep(5)
        
        try:
            webbrowser.open("http://localhost:5000")
            print("✅ Web interface opened in browser")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("   Please manually open: http://localhost:5000")
    
    def show_status(self):
        """Show status and instructions"""
        print("\n" + "=" * 60)
        print("🎉 BuiltByRays™ CFO OS is now running!")
        print("=" * 60)
        print("\n📱 Access your application:")
        print("   • Web Interface: http://localhost:5000")
        print("   • Desktop App: Check for Electron window")
        print("   • API Health: http://localhost:5000/health")
        
        print("\n⚠️  Important:")
        print("   • Add your OpenAI API key to the .env file")
        print("   • The application will continue running")
        print("   • Close this window to stop all services")
        
        print("\n🆘 Need help?")
        print("   • Check README.md for detailed instructions")
        print("   • Contact support@builtbyrays.com")
        print("=" * 60)
    
    def run(self):
        """Main execution function"""
        try:
            self.print_banner()
            
            # Step 1: Install dependencies
            self.check_and_install_dependencies()
            
            # Step 2: Setup environment
            self.setup_environment()
            
            # Step 3: Start vault watcher
            self.start_vault_watcher()
            
            # Step 4: Start Python backend
            if self.start_python_backend():
                # Step 5: Start Electron app (optional)
                self.start_electron_app()
                
                # Step 6: Open web interface
                self.open_web_interface()
                
                # Step 7: Show status
                self.show_status()
                
                # Keep the script running
                print("\n🔄 Services are running. Press Ctrl+C to stop...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping all services...")
                    # Cleanup processes here if needed
            else:
                print("❌ Failed to start backend services")
                input("Press Enter to exit...")
                
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    startup = AutoStartup()
    startup.run() 