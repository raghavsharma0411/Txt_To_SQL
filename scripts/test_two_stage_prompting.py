#!/usr/bin/env python3
"""
Test script to demonstrate and test the two-stage prompting approach.
Stage 1: Identify required tables
Stage 2: Generate SQL with specific schemas
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from utils import identify_required_tables, get_specific_table_schemas, initialize_vector_db, generate_sql
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    print("[OK] Dependencies loaded successfully")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
    exit(1)

def test_stage_one_only():
    """Test only the table identification stage"""
    print("\n" + "="*80)
    print("TESTING STAGE 1: TABLE IDENTIFICATION ONLY")
    print("="*80)
    
    test_questions = [
        "How many residents are active?",
        "Show all companies with their transaction counts",
        "List residents created in the last 30 days",
        "Count transactions by merchant",
        "Show user login history",
        "Find residents with pending applications",
        "Total revenue by payment provider"
    ]
    
    # Test with available LLM (prefer OpenAI, fallback to Gemini)
    llm_type = "openai"
    if not (os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'):
        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
            llm_type = "gemini"
        else:
            print("[ERROR] No API keys configured!")
            return
    
    print(f"[INFO] Using {llm_type.upper()} for table identification")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[TEST {i}] Question: {question}")
        try:
            tables = identify_required_tables(question, llm_type)
            print(f"[RESULT] Identified tables: {tables}")
        except Exception as e:
            print(f"[ERROR] Failed: {e}")

def test_full_two_stage_approach():
    """Test the complete two-stage approach"""
    print("\n" + "="*80)
    print("TESTING COMPLETE TWO-STAGE APPROACH")
    print("="*80)
    
    test_questions = [
        "How many active residents are there?",
        "Show companies with more than 10 transactions",
        "List recent transactions in last 7 days"
    ]
    
    # Test with available LLM
    llm_type = "openai"
    if not (os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'):
        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_api_key_here':
            llm_type = "gemini"
        else:
            print("[ERROR] No API keys configured!")
            return
    
    print(f"[INFO] Using {llm_type.upper()} for full two-stage approach")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"[FULL TEST {i}] Question: {question}")
        print('='*60)
        
        try:
            # This will use the full two-stage approach internally
            sql_result = generate_sql(question, llm_type)
            print(f"\n[FINAL SQL] {sql_result}")
        except Exception as e:
            print(f"[ERROR] Two-stage approach failed: {e}")

def test_schema_retrieval():
    """Test the schema retrieval with specific table names"""
    print("\n" + "="*80)
    print("TESTING STAGE 1.5: SPECIFIC SCHEMA RETRIEVAL")
    print("="*80)
    
    try:
        # Initialize vector database
        collection = initialize_vector_db()
        
        test_cases = [
            {
                "tables": ["rpp_residents", "user"],
                "question": "Show active residents with their user info"
            },
            {
                "tables": ["rppcompany", "rppx9trans"],
                "question": "Companies with transaction data"
            },
            {
                "tables": ["rpp_residents", "rppcompany", "user"],
                "question": "Residents, their companies, and user details"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[SCHEMA TEST {i}] Tables: {test_case['tables']}")
            print(f"Question context: {test_case['question']}")
            
            schemas = get_specific_table_schemas(
                collection, 
                test_case['tables'], 
                test_case['question']
            )
            
            schema_lines = schemas.split('\n')
            print(f"[RESULT] Retrieved {len(schema_lines)} lines of schema")
            print(f"[PREVIEW] {schemas[:200]}...")
            
    except Exception as e:
        print(f"[ERROR] Schema retrieval test failed: {e}")

def main():
    """Run all tests"""
    print("TWO-STAGE PROMPTING TEST SUITE")
    print("="*80)
    
    # Run tests in order of complexity
    test_stage_one_only()
    test_schema_retrieval() 
    test_full_two_stage_approach()
    
    print(f"\n{'='*80}")
    print("ALL TESTS COMPLETED")
    print("="*80)
    print("\n[INFO] Benefits of Two-Stage Approach:")
    print("✅ More accurate table identification")
    print("✅ Precise schema retrieval")  
    print("✅ Better SQL generation quality")
    print("✅ Reduced irrelevant context")
    print("✅ Improved performance")

if __name__ == "__main__":
    main()