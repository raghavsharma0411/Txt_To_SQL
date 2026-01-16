# ============================================================
# STEP 0: Install required packages
# ============================================================
!pip -q install chromadb openai langchain tiktoken langchain-community langchain-openai
!pip install -U langchain-google-genai

# ============================================================
# STEP 1: Imports
# ============================================================
import os
import json
from collections import defaultdict

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================================
# STEP 2: Load table metadata
# ============================================================
with open("tables_metadata.json", "r") as f:
    tables_metadata = json.load(f)

print("Sample metadata:", tables_metadata[:2])

# ============================================================
# STEP 3: Group columns by table
# ============================================================
grouped = defaultdict(list)
for row in tables_metadata:
    grouped[row["TABLE_NAME"]].append(row)

# ============================================================
# STEP 4: Initialize Chroma vector database
# ============================================================
client = chromadb.PersistentClient(path="./schema_db_residents")
collection = client.get_or_create_collection(name="sql_schema")

# ============================================================
# STEP 5: Push table schemas to vector DB
# ============================================================
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

    table_id = f"{table}_schema".lower()

    collection.add(
        documents=[doc],
        metadatas=[metadata],
        ids=[table_id]
    )

print("Schemas pushed to vector DB successfully.")

# ============================================================
# STEP 6: Function to get relevant tables from collection
# ============================================================
def get_relevant_tables(collection, user_question: str, n_results: int = 5) -> str:
    results = collection.query(
        query_texts=[user_question],
        n_results=n_results,
        include=['documents']
    )
    docs = results.get('documents', [[]])[0]
    return "\n".join(docs)

# ============================================================
# STEP 7: Initialize LLMs
# ============================================================
# ---------- OpenAI ----------
os.environ["OPENAI_API_KEY"] = "<YOUR_OPENAI_KEY>"
openai_llm = ChatOpenAI(
    model_name="gpt-5.2",  # or "gpt-3.5-turbo"
    temperature=0
)

# ---------- Gemini ----------
os.environ["GOOGLE_API_KEY"] = "<YOUR_GOOGLE_KEY>"
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0
)

# ============================================================
# STEP 8: Prompt template
# ============================================================
prompt_template = """
You are an expert SQL Server executable query generator.
Use ONLY the provided schema context to answer the question.

### SCHEMA CONTEXT:
{context}

### QUESTION:
{question}

### RESPONSE FORMAT:
Executable SQL Server single-line query only. Do not include any markdown or comments.
"""

# ============================================================
# STEP 9: Function to generate SQL using chosen LLM
# ============================================================
def generate_sql(user_question: str, llm_type: str = "openai") -> str:
    """
    Generate SQL query from user question using the selected LLM.

    Args:
        user_question (str): Natural language question.
        llm_type (str): "openai" or "gemini"

    Returns:
        str: Single-line executable SQL query.
    """
    # Get relevant table schemas
    context_schema = get_relevant_tables(collection, user_question)

    # Prepare prompt
    prompt = prompt_template.format(context=context_schema, question=user_question)

    # Choose LLM
    if llm_type.lower() == "openai":
        response = openai_llm.invoke(prompt)
        raw_sql = response.content[0]['text'] if isinstance(response.content, list) else response.content
    elif llm_type.lower() == "gemini":
        response = gemini_llm.invoke(prompt)
        raw_sql = response.content[0]['text'] if isinstance(response.content, list) else response.content
    else:
        raise ValueError("llm_type must be 'openai' or 'gemini'")

    # Clean SQL into single line
    return " ".join(raw_sql.replace("```sql", "").replace("```", "").split())

# ============================================================
# STEP 10: Example usage
# ============================================================
user_query = "How many residents in last 10 days are in started,in progress,approved,declined"

# Using OpenAI
sql_openai = generate_sql(user_query, llm_type="openai")
print("OpenAI SQL:\n", sql_openai)

# Using Gemini
sql_gemini = generate_sql(user_query, llm_type="gemini")
print("Gemini SQL:\n", sql_gemini)
