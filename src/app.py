import streamlit as st
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Set working directory to project root for Streamlit Cloud compatibility
project_root = Path(__file__).parent.parent
os.chdir(project_root)

from utils import initialize_vector_db, generate_sql, get_database_stats
from config import get_api_keys, validate_api_keys

# ============================================================
# Streamlit App Configuration
# ============================================================
st.set_page_config(
    page_title="Text-to-SQL Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Page Functions
# ============================================================

def show_query_page():
    # Compact header with all info in one row
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
    
    with col1:
        st.markdown("### 🔍 Text-to-SQL Generator")
    
    with col2:
        # Quick status check
        api_keys = get_api_keys()
        openai_configured = api_keys.get('openai_configured', False)
        gemini_configured = api_keys.get('gemini_configured', False)
        
        if not (openai_configured or gemini_configured):
            st.error("⚠️ No API keys configured")
            return
        
        # Model selection
        available_models = []
        if openai_configured:
            available_models.append("OpenAI GPT")
        if gemini_configured:
            available_models.append("Google Gemini")
        
        selected_model = st.selectbox("AI Model:", available_models, label_visibility="collapsed")
    
    with col3:
        st.markdown("**Status:**")
        st.success("Ready")
        
    with col4:
        st.markdown("**Database:**")
        # Initialize database status
        db_path = project_root / "schema_db_residents"
        if not db_path.exists():
            with st.spinner("Init..."):
                try:
                    initialize_vector_db()
                    st.success("Ready")
                except Exception as e:
                    st.error("Error")
        else:
            st.success("Ready")
    
    with col5:
        st.markdown("**Tables:**")
        try:
            stats = get_database_stats()
            st.info(f"{stats.get('total_tables', 0)}")
        except:
            st.info("418")
    
    # Subtle divider
    st.markdown("<hr style='margin: 10px 0; border: 0.5px solid #ddd;'>", unsafe_allow_html=True)
    
    # Compact question input with integrated controls
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        user_question = st.text_area(
            "Enter your question:",
            placeholder="e.g., Give me resident names and dates they are created with their status added in last 2 months",
            height=80,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Align with text area
        generate_btn = st.button("🚀 Generate", type="primary", use_container_width=True)
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Align with text area
        if st.button("💡 Examples", use_container_width=True):
            st.session_state.show_examples = not st.session_state.get('show_examples', False)
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.show_help = not st.session_state.get('show_help', False)
    
    if clear_btn:
        st.rerun()
    
    # Show examples if toggled
    if st.session_state.get('show_examples', False):
        st.markdown("**Quick Examples:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📊 Count by status", key="ex1", use_container_width=True):
                st.session_state.example_question = "Count residents by status"
                st.rerun()
        with col2:
            if st.button("👥 Active residents", key="ex2", use_container_width=True):
                st.session_state.example_question = "How many residents are active?"
                st.rerun()
        with col3:
            if st.button("📅 Last month", key="ex3", use_container_width=True):
                st.session_state.example_question = "Show all residents created in the last month"
                st.rerun()
        with col4:
            if st.button("⏳ Pending apps", key="ex4", use_container_width=True):
                st.session_state.example_question = "Find residents with pending applications"
                st.rerun()
    
    # Show help if toggled
    if st.session_state.get('show_help', False):
        st.info("💡 **Tips:** Use specific terms like 'active residents', 'last 30 days', or 'by status'. The AI understands business terms and will generate optimized SQL queries.")
    
    # Handle example question selection
    if hasattr(st.session_state, 'example_question'):
        user_question = st.session_state.example_question
        delattr(st.session_state, 'example_question')
    
    # Generate SQL query
    if generate_btn and user_question.strip():
        with st.spinner("🔄 Generating SQL query..."):
            try:
                # Determine LLM type
                llm_type = "openai" if selected_model == "OpenAI GPT" else "gemini"
                
                # Generate SQL
                sql_query = generate_sql(user_question, llm_type=llm_type)
                
                # Compact results header
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.success("✅ **SQL Generated Successfully**")
                with col2:
                    st.download_button("📥", sql_query, f"query_{len(st.session_state.get('query_history', []))+1}.sql", mime="text/plain")
                with col3:
                    if st.button("📋 Copy"):
                        st.toast("Copied!", icon="✅")
                with col4:
                    st.metric("", f"{len(sql_query)} chars", label_visibility="collapsed")
                
                # SQL query display (more compact)
                st.code(sql_query, language="sql")
                
                # Save to session state for history
                if 'query_history' not in st.session_state:
                    st.session_state.query_history = []
                
                st.session_state.query_history.append({
                    'question': user_question,
                    'sql': sql_query,
                    'model': selected_model
                })
                
                # Limit history to last 10 queries
                if len(st.session_state.query_history) > 10:
                    st.session_state.query_history = st.session_state.query_history[-10:]
                
            except Exception as e:
                error_message = str(e)
                
                # Display the detailed error message from utils.py
                if error_message.startswith(('🚫', '🔑', '💳', '🌐', '❌')):
                    # Split the error message to display it better
                    lines = error_message.split('\n')
                    for line in lines:
                        if line.strip():
                            if line.startswith(('🚫', '🔑', '💳', '🌐', '❌')):
                                st.error(line)
                            elif line.startswith('**'):
                                st.error(line)
                            elif line.startswith('•'):
                                st.info(line)
                            else:
                                st.write(line)
                else:
                    # Fallback for unexpected errors
                    st.error(f"❌ Error generating SQL: {error_message}")
                    st.info("Please check your API configuration and try again.")
                
                # Show troubleshooting section
                with st.expander("🔧 Troubleshooting Guide"):
                    st.markdown("""
                    **Common Issues & Solutions:**
                    
                    🚫 **Rate Limits**
                    - Wait 1-5 minutes between requests
                    - Check your API usage dashboard
                    
                    🔑 **API Key Problems**
                    - OpenAI keys start with 'sk-proj-' or 'sk-'  
                    - Google keys start with 'AIza'
                    - No spaces before/after key in .env file
                    - Generate new key if current one is invalid
                    
                    💳 **Billing Issues**  
                    - Check API account has sufficient credits
                    - Verify payment method is active
                    
                    🌐 **Network Issues**
                    - Check internet connection
                    - Try refreshing the page
                    - Use VPN if API is blocked in your region
                    """)
                    
                    # Show debug info
                    st.subheader("🔍 Debug Information")
                    st.code(f"Full error: {str(e)}")
                    st.code(f"Selected model: {selected_model}")
                    st.code(f"Question length: {len(user_question)}")
                    
                    # Show API key status for debugging
                    debug_keys = get_api_keys()
                    st.write("**API Key Status:**")
                    st.write(f"OpenAI configured: {debug_keys.get('openai_configured', False)}")
                    st.write(f"Gemini configured: {debug_keys.get('gemini_configured', False)}")
    
    elif generate_btn and not user_question.strip():
        st.warning("⚠️ Please enter a question first!")
    
    # Compact Query History
    if 'query_history' in st.session_state and st.session_state.query_history:
        if st.button(f"📚 Query History ({len(st.session_state.query_history)})", use_container_width=True):
            st.session_state.show_history = not st.session_state.get('show_history', False)
            
        if st.session_state.get('show_history', False):
            for i, item in enumerate(reversed(st.session_state.query_history[-3:]), 1):  # Show only last 3
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.caption(f"**{i}.** {item['question'][:80]}{'...' if len(item['question']) > 80 else ''}")
                        st.code(item['sql'], language="sql")
                    with col2:
                        st.caption(f"Model: {item['model']}")
                        if st.button("🔄", key=f"reuse_{i}", help="Use this question again"):
                            st.session_state.example_question = item['question']
                            st.rerun()

def show_help_page():
    st.title("ℹ️ Help & Examples")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📖 How to Use")
        st.markdown("""
        ### Getting Started
        1. **Configure API Keys** - Go to the Configuration page and set up your OpenAI or Google API keys
        2. **Select AI Model** - Choose between OpenAI GPT or Google Gemini
        3. **Ask Questions** - Enter your questions in natural language
        4. **Generate SQL** - Click the Generate button to get your SQL query
        5. **Use Results** - Copy, download, or use the generated SQL query
        
        ### Tips for Better Results
        - **Be specific** about what data you want
        - **Mention time ranges** if relevant (e.g., "last 30 days")
        - **Include filter criteria** (e.g., "where status is active")
        - **Ask for specific columns** if you don't need all data
        """)
        
        st.header("🎯 Example Questions")
        
        # Categories of examples
        categories = {
            "📊 **Counting & Aggregation**": [
                "How many residents are there in total?",
                "Count residents by status",
                "How many new residents were added this month?",
                "Show the average age of residents",
                "Count residents by city or location"
            ],
            "🔍 **Filtering & Selection**": [
                "Show all active residents",
                "Find residents with pending applications",
                "List residents created in the last 30 days",
                "Show residents with status 'approved'",
                "Find residents older than 25"
            ],
            "📅 **Time-based Queries**": [
                "Show residents created today",
                "List applications from the last week",
                "Count monthly registrations for this year",
                "Find residents updated in the last 10 days",
                "Show oldest resident records"
            ],
            "📋 **Complex Queries**": [
                "Show residents with their application status and dates",
                "List top 10 most recent applications",
                "Find residents who have multiple applications",
                "Show residents grouped by status with counts",
                "List residents with incomplete profiles"
            ]
        }
        
        for category, questions in categories.items():
            with st.expander(category):
                for question in questions:
                    col_q, col_btn = st.columns([4, 1])
                    with col_q:
                        st.write(f"• {question}")
                    with col_btn:
                        if st.button("Try", key=f"try_{question[:20]}"):
                            st.session_state.example_question = question
                            st.switch_page("Query Generator")
        
    with col2:
        st.header("🔧 Quick Reference")
        
        st.subheader("🤖 Available Models")
        st.info("""
        **OpenAI GPT-4**
        - High accuracy
        - Complex queries
        - Better context understanding
        
        **Google Gemini**
        - Fast responses
        - Good for simple queries
        - Cost effective
        """)
        
        st.subheader("🔑 API Keys")
        st.info("""
        **OpenAI**: Get from platform.openai.com
        **Google**: Get from makersuite.google.com
        
        You need at least one API key to use the application.
        """)
        
        st.subheader("💡 Pro Tips")
        st.success("""
        - Use specific table/column names if you know them
        - Mention the exact status values you're looking for
        - Include date formats (YYYY-MM-DD)
        - Ask for specific fields to get cleaner queries
        """)
        
        st.subheader("⚡ Troubleshooting")
        st.warning("""
        **Common Issues:**
        - Rate limits: Wait a few minutes
        - API errors: Check your keys
        - No results: Try rephrasing your question
        - Complex queries: Break into smaller parts
        """)

def show_config_page():
    st.title("⚙️ Configuration")
    
    # API Key Management
    st.header("🔑 API Key Management")
    
    api_keys = get_api_keys()
    openai_configured = api_keys.get('openai_configured', False)
    gemini_configured = api_keys.get('gemini_configured', False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("OpenAI API Key")
        if openai_configured:
            st.success(f"✅ **Configured**")
            st.caption(f"Key: {api_keys.get('openai_preview', '')}")
        else:
            st.error("❌ **Not configured**")
            if api_keys.get('openai'):
                st.warning(f"🔍 Found: {api_keys.get('openai')[:20]}... (check if placeholder)")
    
    with col2:
        st.subheader("Google Gemini API Key")
        if gemini_configured:
            st.success(f"✅ **Configured**")
            st.caption(f"Key: {api_keys.get('gemini_preview', '')}")
        else:
            st.error("❌ **Not configured**")
            if api_keys.get('gemini'):
                st.warning(f"🔍 Found: {api_keys.get('gemini')[:20]}... (check if placeholder)")
    
    # Setup Instructions
    st.header("📋 Setup Instructions")
    
    env_file_exists = (project_root / ".env").exists()
    
    if env_file_exists:
        st.success("✅ **.env file found**")
    else:
        st.error("❌ **.env file not found**")
    
    with st.expander("📝 **Step-by-step Setup Guide**", expanded=not (openai_configured or gemini_configured)):
        st.markdown("""
        ### Step 1: Get Your API Keys
        
        **For OpenAI:**
        1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
        2. Sign in or create an account
        3. Click "Create new secret key"
        4. Copy the key (starts with `sk-proj-` or `sk-`)
        
        **For Google Gemini:**
        1. Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API key"
        4. Copy the key (starts with `AIza`)
        
        ### Step 2: Configure Environment File
        
        1. **Edit the `.env` file** in your project directory
        2. **Add your API key(s):**
        ```
        OPENAI_API_KEY=your_actual_openai_key_here
        GOOGLE_API_KEY=your_actual_google_key_here
        ```
        3. **Save the file**
        4. **Refresh this page**
        
        ### Step 3: Verify Setup
        - At least one API key should show ✅ Configured
        - You can then use the Query Generator
        
        **Note:** You only need ONE API key to start using the application.
        """)
    
    # Database Status
    st.header("🗄️ Database Status")
    
    db_path = project_root / "schema_db_residents"
    schema_file = project_root / "data" / "tables_metadata.json"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if db_path.exists():
            st.success("✅ **Vector DB Ready**")
        else:
            st.warning("⏳ **Vector DB Not Initialized**")
    
    with col2:
        if schema_file.exists():
            st.success("✅ **Schema File Found**")
        else:
            st.error("❌ **Schema File Missing**")
    
    with col3:
        try:
            stats = get_database_stats()
            st.metric("Tables", stats.get('total_tables', 0))
        except:
            st.metric("Tables", "Error")
    
    # System Information
    with st.expander("🖥️ **System Information**"):
        st.write(f"**Python Version:** {sys.version}")
        st.write(f"**Streamlit Version:** {st.__version__}")
        st.write(f"**Working Directory:** {os.getcwd()}")
        st.write(f"**Environment File:** {'.env exists' if env_file_exists else '.env not found'}")

# Import function from utils.py
from utils import get_database_stats

# ============================================================
# Main App
# ============================================================
def main():
    # Navigation
    st.sidebar.title("🧭 Navigation")
    
    # Page selection
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Query Generator", "ℹ️ Help & Examples", "⚙️ Configuration"],
        help="Navigate between different sections of the application"
    )
    
    # Show appropriate page
    if page == "🏠 Query Generator":
        show_query_page()
    elif page == "ℹ️ Help & Examples":
        show_help_page()
    elif page == "⚙️ Configuration":
        show_config_page()
    
    # Compact footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by AI ⚡")

if __name__ == "__main__":
    main()