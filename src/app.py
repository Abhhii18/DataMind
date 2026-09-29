import sys
from pathlib import Path

import streamlit as st

# Add the project root and src folder to the path so the app can import local modules reliably.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = Path(__file__).resolve().parent
for path in [str(ROOT_DIR), str(SRC_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from LLM_QueryEngine import ask_database

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="DataMind | AI-Powered Business Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS FOR MODERN LOOK
# ============================================
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --background-color: #f8fafc;
        --text-color: #1e293b;
    }
    
    /* Hide default Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f1f5f9;
    }
    
    /* Example question cards */
    .example-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .example-card:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🧠 DataMind")
    st.markdown("---")
    
    st.markdown("### 📊 About")
    st.markdown("""
    **DataMind** is an AI-powered business intelligence assistant that lets you query databases using natural language.
    
    Powered by:
    - 🤖 GPT-4o-mini
    - 🗄️ SQLite Database
    - ⚡ Streamlit
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Try These Questions")
    
    example_questions = [
        "How many customers do we have?",
        "What is the most expensive product?",
        "Which city has the most customers?",
        "Show me total sales by category",
        "What were the orders last month?",
        "Which product sold the most units?"
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q}", use_container_width=True):
            st.session_state.clicked_question = q
    
    st.markdown("---")
    
    st.markdown("### 🔗 Links")
    st.markdown("[📖 Documentation](https://github.com/yourusername/datamind)")
    st.markdown("[💼 LinkedIn](https://www.linkedin.com/in/abhishekgupta7184/)")
    st.markdown("[🐙 GitHub](https://github.com/Abhhii18)")

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown('<p class="main-header">🧠 DataMind</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask questions about your e-commerce data in plain English</p>', unsafe_allow_html=True)

# Quick stats (optional - shows database size)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>Customers</h3>
        <p>100</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>Products</h3>
        <p>10</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>Orders</h3>
        <p>500</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# CHAT INTERFACE
# ============================================

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.clicked_question = None

# Check if user clicked an example question
if st.session_state.clicked_question:
    prompt = st.session_state.clicked_question
    st.session_state.clicked_question = None  # Reset
    
    # Add to chat and process
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing your database..."):
            answer = ask_database(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💬 Ask a question about your data..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing your database..."):
            answer = ask_database(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 1rem;'>
    Built with ❤️ using Streamlit, OpenAI, and SQLAlchemy<br>
    © 2026 DataMind | Portfolio Project
</div>
""", unsafe_allow_html=True)