import streamlit as st
import os
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
load_dotenv()

import time
time.sleep(1)  # ek second ka gap

# Removed OpenAI import and client initialization

from backend.ocr import extract_text_from_scanned_pdf
from backend.pdf_loader import extract_pdf_text, get_pdf_metadata, is_scanned_pdf

# Configure page
st.set_page_config(
    page_title="Upload policy documents",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h1 style="margin: 0; font-size: 3rem; font-weight: bold;">
                   File Upload Center
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Upload a PDF or image and chat with its content
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Upload Section
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        accept_multiple_files=False,
        help="Upload a PDF or image file to extract text and interact with it",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file)
        if file_path:
            extracted_text = process_uploaded_file(file_path)
            if extracted_text:
                chat_with_file_llm(extracted_text)

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary directory."""
    try:
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Failed to save the uploaded file: {e}")
        return None

def save_text_to_xml(extracted_text, file_path):
    """Save the extracted text into an XML file."""
    root = ET.Element("Document")
    text_elem = ET.SubElement(root, "ExtractedText")
    text_elem.text = extracted_text

    xml_file_path = file_path + ".xml"
    tree = ET.ElementTree(root)
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
    return xml_file_path

def process_uploaded_file(file_path):
    """Process the uploaded file and extract text."""
    st.markdown("### File Details")
    if file_path.endswith(".pdf"):
        metadata = get_pdf_metadata(file_path)
        st.write("**PDF Metadata:**")
        st.json(metadata)

        if is_scanned_pdf(file_path):
            st.info("The PDF appears to be scanned. Extracting text using OCR...")
            success, ocr_text, _ = extract_text_from_scanned_pdf(file_path)
            if success:
                st.text_area("Extracted Text (OCR)", ocr_text, height=300)
                xml_path = save_text_to_xml(ocr_text, file_path)
                st.success(f"Extracted text saved to XML: {xml_path}")
                return ocr_text
            else:
                st.error("Failed to extract text using OCR.")
                return None
        else:
            st.info("The PDF is a digital document. Extracting text...")
            text = extract_pdf_text(file_path)
            st.text_area("Extracted Text", text, height=300)
            xml_path = save_text_to_xml(text, file_path)
            st.success(f"Extracted text saved to XML: {xml_path}")
            return text
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        st.info("Processing image file...")
        success, ocr_text, _ = extract_text_from_scanned_pdf(file_path)
        if success:
            st.text_area("Extracted Text (OCR)", ocr_text, height=300)
            xml_path = save_text_to_xml(ocr_text, file_path)
            st.success(f"Extracted text saved to XML: {xml_path}")
            return ocr_text
        else:
            st.error("Failed to extract text from the image.")
            return None
    else:
        st.error("Unsupported file type. Please upload a PDF or image file.")
        return None

# Removed query_llm_with_pdf implementation

def chat_with_file_llm(extracted_text):
    """Enable a chat interface for interacting with the extracted text."""
    st.markdown("### Chat with the File")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if user_query := st.chat_input("Ask me something about the file..."):
        st.session_state.messages.append({"role": "user", "content": user_query})

        # No LLM response, just echo or show a message
        response = "LLM functionality has been removed. No automated answer available."
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display response
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
