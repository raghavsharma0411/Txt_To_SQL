#!/usr/bin/env python3
"""
Test script to generate and inspect the vector database.
This helps verify that table schemas are properly stored and retrievable.
"""

import os
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    import chromadb
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    print("[OK] Dependencies loaded successfully")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run: pip install chromadb python-dotenv")
    exit(1)

def load_table_metadata():
    """Load and parse table metadata from JSON file"""
    metadata_file = Path(__file__).parent.parent / "data" / "tables_metadata.json"
    
    if not metadata_file.exists():
        print(f"[ERROR] tables_metadata.json not found at {metadata_file}")
        return None
    
    print(f"[INFO] Loading metadata from: {metadata_file.absolute()}")
    
    with open(metadata_file, "r") as f:
        tables_metadata = json.load(f)
    
    print(f"[OK] Loaded {len(tables_metadata)} metadata records")
    
    # Group by table
    grouped = defaultdict(list)
    for row in tables_metadata:
        grouped[row["TABLE_NAME"]].append(row)
    
    print(f"[OK] Found {len(grouped)} unique tables")
    
    # Show sample tables
    print("\n[TABLES] Sample tables:")
    for i, table_name in enumerate(list(grouped.keys())[:5]):
        column_count = len(grouped[table_name])
        print(f"  {i+1}. {table_name} ({column_count} columns)")
    
    if len(grouped) > 5:
        print(f"  ... and {len(grouped) - 5} more tables")
    
    return grouped

def create_vector_database(grouped_tables):
    """Create and populate the vector database"""
    print(f"\n[DATABASE] Creating vector database...")
    
    # Initialize ChromaDB
    db_path = "./schema_db_residents"
    print(f"Database path: {Path(db_path).absolute()}")
    
    client = chromadb.PersistentClient(path=db_path)
    
    # Delete existing collection if it exists (for clean start)
    try:
        client.delete_collection(name="sql_schema")
        print("[CLEAN] Deleted existing collection")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name="sql_schema",
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"[OK] Created new collection: sql_schema")
    
    # Add documents to collection
    documents = []
    metadatas = []
    ids = []
    id_counter = {}  # Track duplicate IDs
    
    for table_name, columns in grouped_tables.items():
        # Create document text
        doc = f"Table {table_name} has the following columns:\n"
        for col in columns:
            doc += f"- {col['COLUMN_NAME']}: {col['DATA_TYPE']}, nullable: {col['IS_NULLABLE']}\n"
        doc += "\nThis table is part of the database schema for SQL queries."
        
        # Create metadata
        metadata = {
            "table": table_name,
            "column_count": len(columns),
            "type": "table_schema_doc"
        }
        
        # Create unique ID (handle duplicates)
        base_id = f"{table_name}_schema".lower()
        if base_id in id_counter:
            id_counter[base_id] += 1
            table_id = f"{base_id}_{id_counter[base_id]}"
        else:
            id_counter[base_id] = 0
            table_id = base_id
        
        documents.append(doc)
        metadatas.append(metadata)
        ids.append(table_id)
        
        print(f"  [PREP] Prepared: {table_name} ({len(columns)} columns) -> ID: {table_id}")
    
    print(f"\n[INFO] Generated {len(set(ids))} unique IDs from {len(ids)} tables")
    
    # Batch insert all documents
    print(f"\n[INSERT] Inserting {len(documents)} documents into vector database...")
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"[OK] Successfully inserted {len(documents)} documents")
    
    return collection

def inspect_database(collection):
    """Inspect the contents of the vector database"""
    print(f"\n[INSPECT] Inspecting vector database contents...")
    
    # Get basic stats
    count = collection.count()
    print(f"[STATS] Total documents in collection: {count}")
    
    if count == 0:
        print("[ERROR] No documents found in collection!")
        return
    
    # Get all documents (sample)
    try:
        # Get first 5 documents
        sample_docs = collection.get(
            limit=5,
            include=['documents', 'metadatas', 'ids']
        )
        
        print(f"\n[SAMPLE] Sample documents:")
        for i, (doc, metadata, doc_id) in enumerate(zip(
            sample_docs['documents'], 
            sample_docs['metadatas'], 
            sample_docs['ids']
        )):
            print(f"\n  Document {i+1}:")
            print(f"    ID: {doc_id}")
            print(f"    Table: {metadata.get('table', 'Unknown')}")
            print(f"    Columns: {metadata.get('column_count', 'Unknown')}")
            print(f"    Content preview: {doc[:150]}...")
    
    except Exception as e:
        print(f"[ERROR] Error getting sample documents: {e}")

def test_similarity_search(collection):
    """Test similarity search functionality"""
    print(f"\n[TEST] Testing similarity search...")
    
    test_queries = [
        "residents",
        "user status", 
        "applications",
        "How many residents are active?",
        "Count by status"
    ]
    
    for query in test_queries:
        print(f"\n[QUERY] Testing: '{query}'")
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3,
                include=['documents', 'distances', 'metadatas']
            )
            
            docs = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            print(f"   [RESULTS] {len(docs)} documents found")
            
            if docs:
                for i, (doc, distance, metadata) in enumerate(zip(docs, distances, metadatas)):
                    table_name = metadata.get('table', 'Unknown')
                    print(f"   {i+1}. Table: {table_name} (distance: {distance:.4f})")
                    print(f"      Content: {doc[:100]}...")
            else:
                print("   [WARN] No results found!")
                
        except Exception as e:
            print(f"   [ERROR] Error in similarity search: {e}")

def main():
    print("Vector Database Test Script")
    print("=" * 50)
    
    # Step 1: Load metadata
    print("\n[STEP 1] Loading table metadata...")
    grouped_tables = load_table_metadata()
    
    if not grouped_tables:
        print("[ERROR] Failed to load table metadata. Exiting.")
        return
    
    # Step 2: Create vector database
    print("\n[STEP 2] Creating vector database...")
    collection = create_vector_database(grouped_tables)
    
    # Step 3: Inspect database
    print("\n[STEP 3] Inspecting database...")
    inspect_database(collection)
    
    # Step 4: Test similarity search
    print("\n[STEP 4] Testing similarity search...")
    test_similarity_search(collection)
    
    print(f"\n[COMPLETE] Vector database test finished")
    print(f"Database location: {Path('./schema_db_residents').absolute()}")
    print(f"You can now run the Streamlit app: streamlit run app.py")

if __name__ == "__main__":
    main()