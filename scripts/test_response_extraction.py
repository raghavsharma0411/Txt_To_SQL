#!/usr/bin/env python3
"""
Test script to verify response extraction works correctly for both OpenAI and Gemini models.
This helps debug the different response structures.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from utils import generate_sql
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    print("[OK] Dependencies loaded successfully")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run: pip install requirements")
    exit(1)

def test_response_extraction():
    """Test response extraction for both models"""
    print("Response Extraction Test")
    print("=" * 50)
    
    test_question = "How many residents are there?"
    
    # Test OpenAI if configured
    try:
        if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here':
            print("\n[TEST] Testing OpenAI response extraction...")
            try:
                result = generate_sql(test_question, llm_type="openai")
                print(f"[SUCCESS] OpenAI SQL: {result}")
            except Exception as e:
                print(f"[ERROR] OpenAI test failed: {e}")
        else:
            print("\n[SKIP] OpenAI API key not configured")
    except Exception as e:
        print(f"[ERROR] OpenAI test error: {e}")
    
    # Test Gemini if configured  
    try:
        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
            print("\n[TEST] Testing Gemini response extraction...")
            try:
                result = generate_sql(test_question, llm_type="gemini")
                print(f"[SUCCESS] Gemini SQL: {result}")
            except Exception as e:
                print(f"[ERROR] Gemini test failed: {e}")
        else:
            print("\n[SKIP] Gemini API key not configured")
    except Exception as e:
        print(f"[ERROR] Gemini test error: {e}")
    
    print(f"\n[COMPLETE] Response extraction test finished")

if __name__ == "__main__":
    test_response_extraction()