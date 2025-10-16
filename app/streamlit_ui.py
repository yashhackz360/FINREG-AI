import streamlit as st
import os
import json
from src.config import Config
from src.retrieval.embedder import Embedder
from src.retrieval.vector_index import VectorIndex
from src.generation.llm_generator import LLMGenerator
from src.pipeline.rag_pipeline import RAGPipeline

# --- Page Config ---
st.set_page_config(page_title="FinReg AI", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for UI and Sidebar ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0B0F19; color: #E0E0E0; }
    .main .block-container { max-width: 850px; padding-top: 2rem; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    h1 { font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem; color: #E5E7EB; }
    .stChatMessage { background-color: #1E293B; border-radius: 0.75rem; padding: 1rem; margin-bottom: 1rem; border: 1px solid #374151; }
    a { color: #60A5FA; text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* Custom styles for the sidebar summaries */
    [data-testid="stSidebar"] .stExpander {
        background-color: #1F2937;
        border-radius: 0.5rem;
        border: none;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] .stExpander header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #E5E7EB;
    }
    [data-testid="stSidebar"] .stExpander [data-testid="stMarkdownContainer"] {
        font-size: 0.85rem;
        color: #D1D5DB;
    }
</style>
""", unsafe_allow_html=True)

# --- Pipeline Initialization ---
@st.cache_resource
def initialize_pipeline():
    """Initializes and caches the RAG pipeline."""
    config = Config()
    embedder = Embedder(config.embedding_model)
    vector_index = VectorIndex(config.pinecone_config)
    llm_generator = LLMGenerator(api_key=config.groq_api_key, model=config.llm_model)
    return RAGPipeline(embedder, vector_index, llm_generator, config.top_k_retrieval), config

pipeline, config = initialize_pipeline()

# --- Sidebar ---
with st.sidebar:
    st.image("https://placehold.co/400x200/0B0F19/60A5FA?text=FinReg+AI", use_column_width=True)
    st.info(" Rag Powered!! assistant for Indian financial regulations.")
    
    st.markdown("---")
    st.markdown("### 🔴 Latest Ingestions Summary")
    
    summaries_file = config.summaries_file_path
    if os.path.exists(summaries_file):
        with open(summaries_file, 'r') as f:
            try:
                summaries = json.load(f)
                if summaries:
                    # Display the latest 3 summaries in expanders
                    for summary_data in reversed(summaries[-3:]):
                        with st.expander(f"{summary_data['title']}"):
                            st.markdown(summary_data['summary'])
                            st.markdown(f"<a href='{summary_data['url']}' target='_blank'>Read Full Document &rarr;</a>", unsafe_allow_html=True)
                else:
                     st.write("Awaiting first real-time summary...")
            except (json.JSONDecodeError, IndexError):
                st.write("Awaiting first real-time summary...")
    else:
        st.write("Awaiting first real-time summary...")

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 0.5rem;">
            <p style="font-size: 1.1rem; font-weight: 600; color: #FFFFFF; margin-top: 0;">
                Yashwanth K
            </p>
            <a href="https://www.linkedin.com/in/yashwanth-kasarabada-ba4265258/" target="_blank">LinkedIn</a> |
            <a href="https://github.com/yashhackz360" target="_blank">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Main UI ---
st.title("Fintech Regulatory Assistant")

# Initialize and display chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi There I am here you to get acquantied with the  regaultiry infroamtion updated one for indian fintech shoot your questions ?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if query := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating answer..."):
            result = pipeline.execute(query, chat_history=st.session_state.messages)
            answer = result['answer']
            sources = result['sources']
            
            response_content = answer
            if sources:
                response_content += "\n\n**Sources:**\n"
                for source in sources:
                    response_content += f"- [{source['title']}]({source['url']})\n"
            
            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})

