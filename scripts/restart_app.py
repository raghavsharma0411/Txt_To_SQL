#!/usr/bin/env python3
"""
Simple script to restart the Streamlit application.
This ensures that all configuration changes are loaded fresh.
"""

import os
import subprocess
import sys
import time
import signal

def find_streamlit_processes():
    """Find running Streamlit processes"""
    try:
        # On Windows, use tasklist
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            return result.stdout
        else:
            # On Unix-like systems, use ps
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            streamlit_processes = [line for line in result.stdout.split('\n') 
                                 if 'streamlit' in line.lower()]
            return '\n'.join(streamlit_processes)
    except:
        return "Could not check for running processes"

def restart_streamlit():
    """Restart Streamlit application"""
    print("🔄 Restarting Streamlit application...")
    print("\nChecking for running Streamlit processes:")
    processes = find_streamlit_processes()
    print(processes)
    
    print("\n" + "="*50)
    print("🚀 Starting Streamlit application...")
    print("="*50)
    
    try:
        # Start Streamlit
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'src/app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting Streamlit: {e}")
        print("Try running manually: python -m streamlit run app.py")

if __name__ == "__main__":
    restart_streamlit()