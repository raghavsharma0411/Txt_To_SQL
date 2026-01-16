# 🏗️ Project Structure

This document explains the organized folder structure of the Text-to-SQL Generator application.

## 📁 Directory Layout

```
CP_GEN_AI/
├── src/                          # 🏠 Main Application Code
│   ├── app.py                   # Main Streamlit application
│   ├── utils.py                 # Core utility functions (SQL generation, vector DB)
│   └── config.py                # Configuration and API key management
├── data/                         # 📊 Data Files
│   └── tables_metadata.json     # Database schema metadata (7,686 records)
├── scripts/                      # 🛠️ Utility Scripts
│   ├── start_app.bat            # Windows batch file to start app
│   ├── restart_app.py           # Python script to restart app
│   └── test_vector_db.py        # Vector database testing and debugging
├── config/                       # ⚙️ Configuration Templates
│   └── env_template.env         # Environment variables template
├── docs/                         # 📚 Documentation
│   └── README.md                # User guide and setup instructions
├── reference/                    # 📖 Reference Files
│   └── txt_to_sql.py            # Original implementation (for reference)
├── run_app.py                   # 🚀 Main entry point (NEW)
├── PROJECT_STRUCTURE.md         # 📋 This file
├── requirements.txt             # 📦 Python dependencies
├── .env                         # 🔐 Environment variables (user created)
├── schema_db_residents/         # 🗄️ Vector database (auto-generated)
└── __pycache__/                 # 🐍 Python cache (auto-generated)
```

## 📂 Folder Descriptions

### 🏠 `src/` - Main Application Code
Contains the core application files that work together to provide the text-to-SQL functionality:

- **`app.py`** - The main Streamlit web interface with multiple pages:
  - 🏠 Query Generator (main interface)
  - ℹ️ Help & Examples (usage guide)
  - ⚙️ Configuration (API setup)

- **`utils.py`** - Core utility functions:
  - Vector database initialization
  - SQL query generation
  - LLM (OpenAI/Gemini) integration
  - Schema retrieval and processing

- **`config.py`** - Configuration management:
  - API key loading from environment
  - Configuration validation
  - Setup instructions

### 📊 `data/` - Data Files
Contains the database schema information:

- **`tables_metadata.json`** - Complete database schema with:
  - 418 unique tables
  - 7,686 column definitions
  - Data types and constraints

### 🛠️ `scripts/` - Utility Scripts
Helper scripts for development and maintenance:

- **`start_app.bat`** - Windows batch file for easy startup
- **`restart_app.py`** - Python script to restart the application
- **`test_vector_db.py`** - Debug and test vector database functionality

### ⚙️ `config/` - Configuration Templates
Configuration file templates:

- **`env_template.env`** - Template for creating `.env` file with API keys

### 📚 `docs/` - Documentation
User documentation and guides:

- **`README.md`** - Comprehensive setup and usage guide

### 📖 `reference/` - Reference Files
Original implementation files kept for reference:

- **`txt_to_sql.py`** - Original Jupyter notebook-style implementation

## 🚀 How to Run the Application

### Method 1: Main Entry Point (Recommended)
```bash
python run_app.py
```

### Method 2: Direct Streamlit Command
```bash
streamlit run src/app.py
```

### Method 3: Using Scripts
```bash
# Windows
scripts/start_app.bat

# Cross-platform
python scripts/restart_app.py
```

## 🔧 Development Workflow

### Testing Vector Database
```bash
python scripts/test_vector_db.py
```

### Project Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `config/env_template.env` to `.env`
3. Add your API keys to `.env`
4. Run: `python run_app.py`

## 📋 File Dependencies

### Import Relationships
- `src/app.py` imports from `src/utils.py` and `src/config.py`
- `src/utils.py` loads data from `data/tables_metadata.json`
- `scripts/test_vector_db.py` loads data from `data/tables_metadata.json`

### Data Flow
```
data/tables_metadata.json → src/utils.py → Vector Database → SQL Generation
                                     ↓
                            src/app.py → Web Interface
```

## 🔄 Auto-Generated Files
These files/folders are created automatically:
- `schema_db_residents/` - ChromaDB vector database
- `__pycache__/` - Python bytecode cache
- `.streamlit/` - Streamlit configuration (if created)

## 🛡️ Security Notes
- `.env` file contains sensitive API keys - never commit to version control
- `config/env_template.env` is safe to commit (contains no actual keys)
- Vector database (`schema_db_residents/`) can be regenerated if needed

## 📊 Benefits of This Structure

### ✅ **Organization**
- Clear separation of concerns
- Easy to find specific functionality
- Professional project layout

### ✅ **Maintainability**  
- Modular code structure
- Easy to update individual components
- Clear dependencies

### ✅ **Scalability**
- Easy to add new features
- Simple to extend functionality
- Room for future growth

### ✅ **Development**
- Easier debugging
- Better testing capabilities
- Clear development workflow

This organized structure makes the project more professional, maintainable, and easier to understand! 🎉