import os
import json
from collections import defaultdict
import streamlit as st
from pathlib import Path

import chromadb
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================================
# Database and Schema Management
# ============================================================

@st.cache_resource
def initialize_vector_db():
    """
    Initialize and populate the Chroma vector database with table schemas.
    This function is cached to avoid reinitialization on every run.
    
    Returns:
        chromadb.Collection: The initialized collection
    """
    # Load table metadata
    metadata_file = Path(__file__).parent.parent / "data" / "tables_metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"tables_metadata.json not found at {metadata_file}. Please ensure the file is in the data directory.")
    
    with open(metadata_file, "r") as f:
        tables_metadata = json.load(f)
    
    # Group columns by table
    grouped = defaultdict(list)
    for row in tables_metadata:
        grouped[row["TABLE_NAME"]].append(row)
    
    # Initialize Chroma vector database
    client = chromadb.PersistentClient(path="./schema_db_residents")
    collection = client.get_or_create_collection(
        name="sql_schema",
        metadata={"hnsw:space": "cosine"}  # Ensure proper similarity search
    )
    
    # Check if collection is already populated
    try:
        existing_count = collection.count()
        if existing_count > 0:
            print(f"Vector database already contains {existing_count} documents")
            return collection
    except:
        pass
    
    # Push table schemas to vector DB - batch insert for better performance
    documents = []
    metadatas = []
    ids = []
    id_counter = {}  # Track duplicate IDs
    
    for table, cols in grouped.items():
        doc = f"Table {table} has the following columns:\n"
        for c in cols:
            doc += f"- {c['COLUMN_NAME']}: {c['DATA_TYPE']}, nullable: {c['IS_NULLABLE']}\n"
        doc += "\nThis table is part of the database schema for SQL queries."

        metadata = {
            "table": table,
            "column_count": len(cols),
            "type": "table_schema_doc"
        }

        # Create unique ID (handle duplicates)
        base_id = f"{table}_schema".lower()
        if base_id in id_counter:
            id_counter[base_id] += 1
            table_id = f"{base_id}_{id_counter[base_id]}"
        else:
            id_counter[base_id] = 0
            table_id = base_id

        documents.append(doc)
        metadatas.append(metadata)
        ids.append(table_id)
    
    # Batch insert all documents (more efficient)
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully inserted {len(documents)} table schemas into vector database.")
    
    print("Schemas pushed to vector DB successfully.")
    return collection

def get_relevant_tables(collection, user_question: str, n_results: int = 5) -> str:
    """
    Get relevant table schemas from the vector database based on user question.
    
    Args:
        collection: Chroma collection
        user_question (str): User's natural language question
        n_results (int): Number of relevant results to retrieve
        
    Returns:
        str: Concatenated relevant table schemas
    """
    print("----------------get_relevant_tables----------------")
    print(f"User question: {user_question}")
    print(f"Collection count: {collection.count()}")
    
    # Test: Get all documents to see what's in the collection
    try:
        all_docs = collection.get(include=['documents', 'metadatas'])
        print(f"Total documents in collection: {len(all_docs.get('documents', []))}")
        if all_docs.get('documents'):
            print(f"Sample document: {all_docs['documents'][0][:200]}...")
    except Exception as e:
        print(f"Error getting all docs: {e}")
    
    print("--------------------------------")
    
    results = collection.query(
        query_texts=[user_question],
        n_results=n_results,
        include=['documents', 'distances']
    )
    
    print(f"Query results: {results}")
    print("--------------------------------")
    
    docs = results.get('documents', [[]])[0]
    distances = results.get('distances', [[]])[0]
    
    print(f"Retrieved docs count: {len(docs)}")
    print(f"Distances: {distances}")
    print(f"First few docs: {docs[:2] if docs else 'None'}")
    print("--------------------------------")
    
    # Fallback: if no docs found via similarity search, get some random docs
    if not docs:
        print("No docs found via similarity search, trying fallback...")
        try:
            fallback_docs = collection.get(limit=n_results, include=['documents'])
            docs = fallback_docs.get('documents', [])
            print(f"Fallback retrieved {len(docs)} documents")
        except Exception as e:
            print(f"Fallback also failed: {e}")
    
    return "\n".join(docs)

# ============================================================
# LLM Configuration and Management
# ============================================================

@st.cache_resource
def get_openai_llm():
    """
    Initialize and cache OpenAI LLM.
    
    Returns:
        ChatOpenAI: OpenAI language model instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please configure it in config.py")
    
    return ChatOpenAI(
        model_name="gpt-5.2",  # Using gpt-4 instead of the non-existent gpt-5.2
        temperature=0,
        api_key=api_key
    )

@st.cache_resource
def get_gemini_llm():
    """
    Initialize and cache Gemini LLM.
    
    Returns:
        ChatGoogleGenerativeAI: Gemini language model instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not found. Please configure it in config.py")
    
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",  # Using available model name
        temperature=0,
        google_api_key=api_key
    )

# ============================================================
# SQL Generation
# ============================================================

def identify_required_tables(user_question: str, llm_type: str = "openai") -> list:
    """
    Stage 1: Identify which tables are needed for the user question.
    
    Args:
        user_question (str): Natural language question
        llm_type (str): "openai" or "gemini"
        
    Returns:
        list: List of table names required for the query
    """
    table_identification_prompt = """
You are an expert database analyst for RPP (Real Property Platform) system.

### PRIMARY TABLES IN SYSTEM:
- rppcompany: Company/organization data
- rppx9trans: Transaction records  
- rppmerchantinfo: Merchant information
- rppx9providers: Payment providers
- rpp_residents: Resident data
- user: User accounts and authentication
- rpp_properties: Property information

### YOUR TASK:
Analyze the user question and identify which tables are needed to answer it.
You can assume some other tables also that are not mentioned in the primary tables but are related to the user question.
### USER QUESTION:
{question}

### RESPONSE FORMAT:
Return ONLY a comma-separated list of table names (no explanations).
Example: rppcompany,rpp_residents,user

### GUIDELINES:
- For residents: Include rpp_residents
- For companies: Include rppcompany
- For transactions/payments: Include rppx9trans, rppmerchantinfo, rppx9providers  
- For historical data: Include *_history tables
- Always include user table if tracking who created/updated records

Table Names:"""

    prompt = table_identification_prompt.format(question=user_question)
    
    try:
        # Get LLM response for table identification
        if llm_type.lower() == "openai":
            llm = get_openai_llm()
            response = llm.invoke(prompt)
            raw_response = response.content if hasattr(response, 'content') else str(response)
        elif llm_type.lower() == "gemini":
            llm = get_gemini_llm()
            response = llm.invoke(prompt)
            if hasattr(response, 'content'):
                if isinstance(response.content, list) and len(response.content) > 0:
                    if isinstance(response.content[0], dict) and 'text' in response.content[0]:
                        raw_response = response.content[0]['text']
                    else:
                        raw_response = str(response.content[0])
                else:
                    raw_response = response.content
            else:
                raw_response = str(response)
        else:
            raise ValueError("llm_type must be 'openai' or 'gemini'")
        
        # Parse table names from response
        table_names = [name.strip() for name in raw_response.split(',')]
        table_names = [name for name in table_names if name]  # Remove empty strings
        
        print(f"[STAGE 1] Identified tables: {table_names}")
        return table_names
        
    except Exception as e:
        print(f"[STAGE 1 ERROR] Failed to identify tables: {e}")
        # Fallback to common tables
        return ["rpp_residents", "rppcompany", "user"]

def get_specific_table_schemas(collection, table_names: list, user_question: str, n_results: int = 10) -> str:
    """
    Stage 1.5: Get schemas for specific tables with high priority, plus some similar ones.
    
    Args:
        collection: Chroma collection
        table_names (list): Specific table names to prioritize
        user_question (str): Original user question for similarity search
        n_results (int): Total number of results to return
        
    Returns:
        str: Concatenated relevant table schemas
    """
    print("----------------get_specific_table_schemas----------------")
    print(f"Priority tables: {table_names}")
    print("--------------------------------")
    
    all_schemas = []
    found_table_ids = set()
    
    # Step 1: Get exact matches for priority tables
    for table_name in table_names:
        table_id = f"{table_name.lower()}_schema"
        try:
            specific_result = collection.get(
                ids=[table_id],
                include=['documents', 'metadatas']
            )
            if specific_result['documents']:
                all_schemas.extend(specific_result['documents'])
                found_table_ids.add(table_id)
                print(f"[PRIORITY] Found exact match: {table_name}")
        except Exception as e:
            print(f"[PRIORITY] Exact match failed for {table_name}: {e}")
    
    # Step 2: Search for similar table names if exact matches not found
    for table_name in table_names:
        if f"{table_name.lower()}_schema" not in found_table_ids:
            try:
                # Search for tables with similar names
                search_results = collection.query(
                    query_texts=[f"Table {table_name}"],
                    n_results=2,
                    include=['documents', 'metadatas', 'ids']
                )
                
                docs = search_results.get('documents', [[]])[0]
                ids = search_results.get('ids', [[]])[0]
                
                for doc, doc_id in zip(docs, ids):
                    if doc_id not in found_table_ids:
                        all_schemas.append(doc)
                        found_table_ids.add(doc_id)
                        print(f"[SIMILARITY] Found similar match for {table_name}: {doc_id}")
                        
            except Exception as e:
                print(f"[SIMILARITY] Search failed for {table_name}: {e}")
    
    # Step 3: Fill remaining slots with general similarity search
    remaining_slots = n_results - len(all_schemas)
    if remaining_slots > 0:
        try:
            general_results = collection.query(
                query_texts=[user_question],
                n_results=remaining_slots + 5,  # Get extra to filter out duplicates
                include=['documents', 'ids']
            )
            
            docs = general_results.get('documents', [[]])[0]
            ids = general_results.get('ids', [[]])[0]
            
            added_count = 0
            for doc, doc_id in zip(docs, ids):
                if doc_id not in found_table_ids and added_count < remaining_slots:
                    all_schemas.append(doc)
                    found_table_ids.add(doc_id)
                    added_count += 1
                    print(f"[GENERAL] Added general match: {doc_id}")
                    
        except Exception as e:
            print(f"[GENERAL] General similarity search failed: {e}")
    
    print(f"[RESULT] Total schemas retrieved: {len(all_schemas)}")
    print("--------------------------------")
    
    return "\n".join(all_schemas)

def generate_sql(user_question: str, llm_type: str = "openai") -> str:
    """
    Generate SQL query from user question using the selected LLM.

    Args:
        user_question (str): Natural language question.
        llm_type (str): "openai" or "gemini"

    Returns:
        str: Single-line executable SQL query.
    
    Raises:
        Exception: With detailed error message for different types of API errors
    """
    try:
        # Initialize vector database
        collection = initialize_vector_db()

        print("================== TWO-STAGE SQL GENERATION ==================")
        print(f"User question: {user_question}")
        print("===============================================================")

        # STAGE 1: Identify required tables
        print("\n[STAGE 1] Identifying required tables...")
        required_tables = identify_required_tables(user_question, llm_type)
        
        # STAGE 1.5: Get specific table schemas with priority
        print(f"\n[STAGE 1.5] Retrieving schemas for priority tables: {required_tables}")
        context_schema = get_specific_table_schemas(collection, required_tables, user_question)
        
        print(f"\n[STAGE 2] Schema context length: {len(context_schema)}")
        print(f"Context preview: {context_schema[:300]}..." if context_schema else "No context retrieved!")
        print("--------------------------------")
        
        # STAGE 2: Generate SQL with specific schemas
        print(f"\n[STAGE 2] Generating SQL query with identified table schemas...")
        
        prompt_template = """
You are an expert SQL Server query generator for RPP (Real Property Platform) database.

STAGE 2: SQL GENERATION
You have been provided with the EXACT table schemas needed for this query. Use ONLY these schemas.

### CRITICAL BUSINESS RULES:
1. **Flag Values**: All boolean flags use -1 for TRUE/ACTIVE and 0 for FALSE/INACTIVE
   - Example: WHERE isactive = -1 (not = 1)
   - Example: WHERE isdeleted = 0 (not = false)

2. **Foreign Key Convention**: FK columns start with 'h' and point to target table's 'hmy' column
   - Example: hrppcompany → rppcompany.hmy
   - Example: huser → user.hmy
   - Always use these relationships for JOINs

3. **Audit Columns** (present in all tables):
   - dtcreated, dtupdated: datetime stamps
   - hcreated, hupdated: reference user.hmy (who created/updated)
   - Use for filtering by date ranges or tracking changes

4. **Primary Tables** (already identified and provided below):
   - rppcompany: Company/organization data
   - rppx9trans: Transaction records  
   - rppmerchantinfo: Merchant information
   - rppx9providers: Payment providers
   - rpp_residents: Resident data

### OPTIMIZATION REQUIREMENTS:
- Use table aliases for readability (c for company, r for residents, etc.)
- Format dates as 'YYYY-MM-DD'
- Always use h-prefix foreign keys for JOINs

### RELEVANT TABLE SCHEMAS:
{context}

### USER QUESTION:
{question}

### RESPONSE:
Generate ONLY the executable SQL Server query. No markdown, comments, or explanations.

SQL:"""
        
        prompt = prompt_template.format(context=context_schema, question=user_question)

        print("--------------------------------")
        print("Prompt: ", prompt)
        print("--------------------------------")
        
        # Choose and use LLM
        if llm_type.lower() == "openai":
            llm = get_openai_llm()
            response = llm.invoke(prompt)
            print("--------------------------------")
            print("OpenAI Response type:", type(response))
            print("OpenAI Response content:", response.content if hasattr(response, 'content') else response)
            print("--------------------------------")
            
            # Extract content from OpenAI response
            if hasattr(response, 'content'):
                raw_sql = response.content
            else:
                raw_sql = str(response)
                
        elif llm_type.lower() == "gemini":
            llm = get_gemini_llm()
            response = llm.invoke(prompt)
            print("--------------------------------")
            print("Gemini Response type:", type(response))
            print("Gemini Response:", response)
            print("Gemini Response content:", response.content if hasattr(response, 'content') else "No content attr")
            print("--------------------------------")
            
            # Extract content from Gemini response (different structure)
            if hasattr(response, 'content'):
                # Check if content is a list with text dictionary
                if isinstance(response.content, list) and len(response.content) > 0:
                    if isinstance(response.content[0], dict) and 'text' in response.content[0]:
                        raw_sql = response.content[0]['text']
                    else:
                        # Fallback: content is a list but not the expected structure
                        raw_sql = str(response.content[0])
                else:
                    # Fallback: content is not a list
                    raw_sql = response.content
            else:
                raw_sql = str(response)
        else:
            raise ValueError("llm_type must be 'openai' or 'gemini'")
        
        # Clean SQL into single line and remove markdown formatting
        cleaned_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
        return " ".join(cleaned_sql.split())
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle specific API errors with user-friendly messages
        if "rate limit" in error_msg or "quota" in error_msg:
            raise Exception("🚫 API Rate Limit Exceeded!\n\nThis means you've used up your API quota or are making requests too quickly.\n\n**Solutions:**\n• Wait a few minutes and try again\n• Check your API billing/usage limits\n• Try using the other AI model if available")
        
        elif "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg:
            raise Exception(f"🔑 API Authentication Error!\n\nYour {llm_type.upper()} API key seems to be invalid.\n\n**Solutions:**\n• Double-check your API key in the .env file\n• Make sure there are no extra spaces\n• Generate a new API key if needed\n\n**Original error:** {str(e)}")
        
        elif "billing" in error_msg or "payment" in error_msg:
            raise Exception(f"💳 API Billing Issue!\n\nThere's a problem with your {llm_type.upper()} account billing.\n\n**Solutions:**\n• Check your API account billing status\n• Add payment method if required\n• Try the other AI model if available\n\n**Original error:** {str(e)}")
        
        elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            raise Exception(f"🌐 Network Connection Error!\n\n**Solutions:**\n• Check your internet connection\n• Try again in a few moments\n• Use a VPN if API is blocked in your region\n\n**Original error:** {str(e)}")
        
        else:
            raise Exception(f"❌ Unexpected Error with {llm_type.upper()}!\n\n**Error Details:** {str(e)}\n\n**Solutions:**\n• Try the other AI model if available\n• Check your API key configuration\n• Contact support if the issue persists")

# ============================================================
# Utility Functions
# ============================================================

def validate_sql_query(sql_query: str) -> bool:
    """
    Basic validation for SQL query.
    
    Args:
        sql_query (str): SQL query to validate
        
    Returns:
        bool: True if query appears valid
    """
    if not sql_query.strip():
        return False
    
    # Check for basic SQL keywords
    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
    has_keyword = any(keyword in sql_query.upper() for keyword in sql_keywords)
    
    return has_keyword

def get_database_stats():
    """
    Get statistics about the vector database.
    
    Returns:
        dict: Database statistics
    """
    try:
        collection = initialize_vector_db()
        count = collection.count()
        return {
            "total_tables": count,
            "database_path": "./schema_db_residents",
            "status": "active"
        }
    except Exception as e:
        return {
            "total_tables": 0,
            "database_path": "./schema_db_residents",
            "status": f"error: {str(e)}"
        }

def format_sql_query(sql_query: str) -> str:
    """
    Format SQL query for better readability.
    
    Args:
        sql_query (str): Raw SQL query
        
    Returns:
        str: Formatted SQL query
    """
    # Basic SQL formatting
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN']
    
    formatted = sql_query
    for keyword in keywords:
        formatted = formatted.replace(f' {keyword} ', f'\n{keyword} ')
        formatted = formatted.replace(f'{keyword} ', f'{keyword} ')
    
    return formatted.strip()