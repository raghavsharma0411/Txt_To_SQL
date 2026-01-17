# Streamlit Deployment Guide

## Deployment on Streamlit Cloud

### Step 1: Push Your Code to GitHub
Ensure your repository is on GitHub with the following structure:
```
project-root/
├── streamlit_app.py          ← Main entry point
├── .streamlit/
│   └── config.toml          ← Streamlit configuration
├── requirements.txt         ← Python dependencies
├── src/
│   ├── app.py              ← Main app logic
│   ├── config.py           ← Configuration management
│   └── utils.py            ← Utility functions
├── data/
│   └── tables_metadata.json ← Database schema
└── .gitignore              ← Files to exclude
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository, branch, and app file (`streamlit_app.py`)
4. Click "Deploy"

### Step 3: Configure Secrets
In Streamlit Cloud dashboard:
1. Go to your app settings (gear icon)
2. Click "Secrets"
3. Add your API keys in the format:
```toml
OPENAI_API_KEY = "your_openai_key_here"
GOOGLE_API_KEY = "your_gemini_key_here"
```

### Step 4: Verify Deployment
- Check the app URL provided by Streamlit
- Verify all pages load correctly
- Test the query generation feature

## Local Development

To run locally:
```bash
cd /path/to/project
python -m streamlit run streamlit_app.py
```

## Troubleshooting

### App doesn't display
- ✅ Ensure `streamlit_app.py` exists in the project root
- ✅ Check `.streamlit/config.toml` is present
- ✅ Verify all dependencies are in `requirements.txt`

### API keys not working
- ✅ Use Streamlit Secrets (not `.env` in cloud)
- ✅ Verify keys are added in app settings → Secrets
- ✅ Restart the app after adding secrets

### Database initialization fails
- ✅ Ensure `data/tables_metadata.json` is committed to git
- ✅ Check database path is accessible
- ✅ Verify file permissions

### Import errors
- ✅ Check `sys.path` modifications in `streamlit_app.py`
- ✅ Ensure all modules are in correct directories
- ✅ Verify requirements.txt has all dependencies

## Environment Variables for Streamlit Cloud

Use Streamlit's built-in secrets management instead of `.env`:

**In Streamlit Cloud dashboard:**
Settings → Secrets → Add your configuration
```toml
OPENAI_API_KEY = "sk-proj-xxxxx"
GOOGLE_API_KEY = "AIzaxxxxx"
```

These will be automatically available as environment variables.
