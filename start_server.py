#!/usr/bin/env python3
"""
Pendo Data Generation Backend Server
Easy startup script for development and production
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import playwright
        import pydantic
        import aiofiles
        print("✅ All Python dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_playwright():
    """Check if Playwright browsers are installed"""
    try:
        result = subprocess.run(['playwright', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Playwright installed: {result.stdout.strip()}")
        
        # Check if browsers are installed
        result = subprocess.run(['playwright', 'install', '--dry-run', 'chromium'], 
                              capture_output=True, text=True)
        if "is already installed" in result.stderr or result.returncode == 0:
            print("✅ Chromium browser is ready")
            return True
        else:
            print("❌ Chromium browser not installed")
            print("Run: playwright install chromium")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Playwright CLI not found")
        print("Run: pip install playwright && playwright install chromium")
        return False

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    
    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ backend/main.py not found. Make sure you're in the project root directory.")
        return False
    
    # Prepare uvicorn command
    cmd = [
        "uvicorn", 
        "backend.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print("🔄 Auto-reload: enabled" if reload else "🔄 Auto-reload: disabled")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main startup function"""
    print("🎭 Pendo Data Generation Backend")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_playwright():
        # In production (Railway/Docker), browsers should already be installed
        # If not, try to install them automatically without prompting
        print("🔧 Playwright browsers not found, attempting automatic installation...")
        try:
            subprocess.run(['playwright', 'install', 'chromium'], check=True)
            print("✅ Playwright browsers installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Playwright browsers")
            # Don't exit in production - let the app start and handle browser errors gracefully
            print("⚠️  Starting server without browsers (simulations may fail)")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Start Pendo Data Generation Backend")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port to bind to") 
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    # Start the server
    success = start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 