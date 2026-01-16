#!/usr/bin/env python3
"""
Main entry point for the Text-to-SQL Generator application.
This script starts the Streamlit application from the organized folder structure.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit application"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    app_file = project_root / "src" / "app.py"
    
    # Check if the app file exists
    if not app_file.exists():
        print(f"[ERROR] Application file not found at {app_file}")
        print("Please ensure the project structure is correct.")
        sys.exit(1)
    
    # Change to project root directory
    os.chdir(project_root)
    
    print("[INFO] Starting Text-to-SQL Generator...")
    print(f"[INFO] Project root: {project_root}")
    print(f"[INFO] App file: {app_file}")
    print("-" * 50)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            str(app_file),
            '--server.headless', 'true'
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] Application stopped by user")
    except FileNotFoundError:
        print("[ERROR] Streamlit not found. Please install it:")
        print("pip install streamlit")
    except Exception as e:
        print(f"[ERROR] Error starting application: {e}")

if __name__ == "__main__":
    main()