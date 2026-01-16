import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads .env file automatically
except ImportError:
    # dotenv not installed, will use system environment variables only
    pass

# ============================================================
# API Key Configuration
# ============================================================

def get_api_keys():
    """
    Get API keys from environment variables or return empty dict if not found.
    
    Returns:
        dict: Dictionary containing API keys and their status
    """
    openai_key = os.getenv('OPENAI_API_KEY', '')
    gemini_key = os.getenv('GOOGLE_API_KEY', '')
    
    return {
        'openai': openai_key,
        'gemini': gemini_key,
        'openai_configured': bool(openai_key and openai_key != 'your_openai_api_key_here'),
        'gemini_configured': bool(gemini_key and gemini_key != 'your_google_api_key_here'),
        'openai_preview': openai_key[:10] + '...' if openai_key and openai_key != 'your_openai_api_key_here' else '',
        'gemini_preview': gemini_key[:10] + '...' if gemini_key and gemini_key != 'your_google_api_key_here' else ''
    }

def validate_api_keys():
    """
    Validate that at least one API key is configured.
    
    Returns:
        tuple: (is_valid, missing_keys)
    """
    api_keys = get_api_keys()
    missing_keys = []
    
    if not api_keys['openai']:
        missing_keys.append('OPENAI_API_KEY')
    if not api_keys['gemini']:
        missing_keys.append('GOOGLE_API_KEY')
    
    is_valid = len(missing_keys) < 2  # At least one key should be present
    return is_valid, missing_keys

def set_environment_keys():
    """
    Set environment variables for API keys.
    This is called automatically when the module is imported.
    """
    api_keys = get_api_keys()
    
    if api_keys['openai']:
        os.environ["OPENAI_API_KEY"] = api_keys['openai']
    if api_keys['gemini']:
        os.environ["GOOGLE_API_KEY"] = api_keys['gemini']

# ============================================================
# Configuration Instructions
# ============================================================

SETUP_INSTRUCTIONS = """
🔧 API Key Setup Instructions:

To use this application, you need to set up your API keys. You have several options:

OPTION 1 - Environment Variables (Recommended):
1. Create a .env file in the project root
2. Add your API keys:
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
3. Install python-dotenv: pip install python-dotenv

OPTION 2 - System Environment Variables:
Windows:
   set OPENAI_API_KEY=your_openai_api_key_here
   set GOOGLE_API_KEY=your_google_api_key_here

macOS/Linux:
   export OPENAI_API_KEY=your_openai_api_key_here
   export GOOGLE_API_KEY=your_google_api_key_here

OPTION 3 - Direct in this file (Not recommended for production):
Uncomment and modify the lines below:

# os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
# os.environ["GOOGLE_API_KEY"] = "your_google_api_key_here"

Note: You need at least one API key to use the application.
"""

# ============================================================
# Uncomment the lines below to set API keys directly (NOT RECOMMENDED)
# ============================================================
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
# os.environ["GOOGLE_API_KEY"] = "your_google_api_key_here"

# Automatically set environment variables when module is imported
set_environment_keys()

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
    is_valid, missing = validate_api_keys()
    if is_valid:
        print("✅ API keys configured successfully!")
    else:
        print(f"❌ Missing API keys: {', '.join(missing)}")