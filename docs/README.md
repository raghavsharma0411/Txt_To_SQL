# 🔍 Text-to-SQL Query Generator

A Streamlit web application that converts natural language questions into SQL queries using AI models (OpenAI GPT and Google Gemini).

## ✨ Features

- **Natural Language to SQL**: Convert your questions into executable SQL queries
- **Multiple AI Models**: Choose between OpenAI GPT and Google Gemini
- **Interactive Web Interface**: User-friendly Streamlit interface
- **Query History**: Keep track of your previous queries
- **Vector Database**: Intelligent schema matching using ChromaDB
- **Real-time Processing**: Fast query generation with caching

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- At least one API key (OpenAI or Google)

### Installation Steps

1. **Clone or download the project files**
   ```bash
   # Make sure you have all these files in your project directory:
   # - app.py
   # - utils.py
   # - config.py
   # - requirements.txt
   # - tables_metadata.json
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API Keys** (Choose one method)

   **Method A: Environment Variables (Recommended)**
   ```bash
   # Windows
   set OPENAI_API_KEY=your_openai_api_key_here
   set GOOGLE_API_KEY=your_google_api_key_here
   
   # macOS/Linux
   export OPENAI_API_KEY=your_openai_api_key_here
   export GOOGLE_API_KEY=your_google_api_key_here
   ```

   **Method B: Create .env file**
   ```bash
   # Create a .env file in the project root with:
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   **Method C: Direct in config.py (Not recommended)**
   - Open `config.py`
   - Uncomment and update the API key lines at the bottom

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will open automatically at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

## 🔑 Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the generated key

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the generated key

**Note:** You need at least one API key to use the application.

## 📱 How to Use

1. **Select AI Model**: Choose between OpenAI GPT or Google Gemini in the sidebar
2. **Enter Question**: Type your natural language question in the text area
3. **Generate SQL**: Click the "Generate SQL" button
4. **Copy Query**: Use the generated SQL query in your database

### Example Questions
- "How many residents are active?"
- "Show all residents created in the last month"
- "Count residents by status"
- "Find residents with pending applications"

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── utils.py              # Core functions and utilities
├── config.py             # API key configuration
├── requirements.txt      # Python dependencies
├── tables_metadata.json  # Database schema metadata
├── README.md             # This file
└── schema_db_residents/  # ChromaDB vector database (auto-created)
```

## ⚙️ Configuration

### Model Settings
- **OpenAI Model**: GPT-4 (configurable in utils.py)
- **Gemini Model**: gemini-1.5-pro (configurable in utils.py)
- **Temperature**: 0 (for consistent results)

### Database Settings
- **Vector DB**: ChromaDB with persistent storage
- **Schema File**: tables_metadata.json
- **Cache**: Streamlit caching for better performance

## 🔧 Customization

### Changing AI Models
Edit the model names in `utils.py`:
```python
# For OpenAI
model_name="gpt-4"  # Change to "gpt-3.5-turbo" for cheaper option

# For Gemini  
model="gemini-1.5-pro"  # Change to other available models
```

### Modifying Prompt Template
Update the prompt template in `utils.py` in the `generate_sql()` function to customize how the AI generates queries.

### Adding More Metadata
Replace or update `tables_metadata.json` with your database schema information.

## 🚨 Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Check that your API keys are set correctly
   - Verify the environment variables or .env file

2. **"tables_metadata.json not found"**
   - Ensure the metadata file is in the project root directory
   - Check the file name and format

3. **"Vector database error"**
   - Delete the `schema_db_residents` folder and restart the app
   - Check file permissions

4. **Module import errors**
   - Run `pip install -r requirements.txt` again
   - Check Python version (3.8+ required)

### Performance Tips
- The vector database is cached for better performance
- First run may take longer as it initializes the database
- Subsequent runs will be faster

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all files are present in the project directory
3. Ensure API keys are correctly configured
4. Check the Streamlit console for error messages

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables or .env files
- Keep your API keys secure and rotate them regularly
- Monitor your API usage to avoid unexpected charges

## 📄 License

This project is for educational and development purposes. Make sure to comply with the terms of service of OpenAI and Google when using their APIs.