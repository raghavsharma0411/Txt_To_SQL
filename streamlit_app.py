#!/usr/bin/env python3
"""
Streamlit Cloud entry point for the Text-to-SQL Generator application.
This file is specifically named for Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
