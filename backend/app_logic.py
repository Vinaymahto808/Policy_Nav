# backend/app_logic.py

import streamlit as st
import os
import tempfile
from backend.text_processor import TextChunker
from backend.pdf_loader import extract_pdf_text
from backend.ocr import extract_text_from_image

def initialize_session_state():
    """Initialize session state for the Streamlit app."""
    if "chunks" not in st.session_state:
        st.session_state.chunks = None
    if "searcher" not in st.session_state:
        st.session_state.searcher = None
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "chunking_method" not in st.session_state:
        st.session_state.chunking_method = "sentences"

def configure_chunking():
    """Configure chunking settings based on user input."""
    col1, col2, col3 = st.columns(3)
    with col1:
        chunk_size = st.slider("Chunk Size (characters)", 500, 3000, 1000, 100)
    with col2:
        overlap = st.slider("Overlap (characters)", 0, 500, 200, 50)
    with col3:
        chunking_method = st.selectbox("Chunking Method", ["sentences", "paragraphs"], 
                                        index=0 if st.session_state.chunking_method == "sentences" else 1)

    return chunk_size, overlap, chunking_method

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory."""
    try:
        # Create temp_files directory if it doesn't exist
        temp_dir = "temp_files"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save file with original name
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def process_uploaded_file(file_path):
    """Process uploaded file and extract text."""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            # Extract text from PDF
            extracted_text = extract_pdf_text(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            # Extract text from image using OCR
            success, extracted_text, _ = extract_text_from_image(file_path)
            if not success:
                st.error("Failed to extract text from image")
                return None
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
        
        return extracted_text.strip() if extracted_text else None
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def process_document(uploaded_file):
    """Process the uploaded document and extract text."""
    file_path = save_uploaded_file(uploaded_file)
    if file_path:
        extracted_text = process_uploaded_file(file_path)
        if extracted_text:
            # Use default chunking settings
            chunker = TextChunker(chunk_size=1000, overlap=200)
            
            # Use chunking method from session state
            chunking_method = st.session_state.get('chunking_method', 'sentences')
            
            if chunking_method == 'sentences':
                chunks = chunker.chunk_by_sentences(extracted_text)
            else:
                chunks = chunker.chunk_by_paragraphs(extracted_text)
            
            return chunks
    return None