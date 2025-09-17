
import streamlit as st
from backend.app_logic import initialize_session_state, configure_chunking, process_document
from backend.text_processor import TextSearcher

def main():
    st.set_page_config(
        page_title="PDF Text Extractor",
        page_icon="📄",
        layout="wide"
    )
    
    st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h1 style="margin: 0; font-size: 3rem; font-weight: bold;">
                   📄 PDF Text Extractor
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Upload PDF or image files to extract text content
            </p>
        </div>
        """,
                unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Upload Section
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        accept_multiple_files=False,
        help="Upload a PDF or image file to extract text and interact with it",
        type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
        with st.spinner("Processing document..."):
            chunks = process_document(uploaded_file)
            
        if chunks:
            st.session_state.chunks = chunks
            st.session_state.searcher = TextSearcher(chunks)
            
            st.success(f"Document processed successfully! Found {len(chunks)} text chunks.")
            
            # Display chunks
            st.subheader("📝 Extracted Text")
            
            # Show full text
            full_text = "\n\n".join([chunk['text'] for chunk in chunks])
            st.text_area("Full Extracted Text", value=full_text, height=300)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as TXT",
                    data=full_text,
                    file_name=f"{uploaded_file.name}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Create XML format
                xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<document>
    <metadata>
        <filename>{uploaded_file.name}</filename>
        <chunks_count>{len(chunks)}</chunks_count>
    </metadata>
    <content>
        <full_text><![CDATA[{full_text}]]></full_text>
        <chunks>
"""
                for chunk in chunks:
                    xml_content += f"""            <chunk id="{chunk['id']}">
                <text><![CDATA[{chunk['text']}]]></text>
                <word_count>{chunk['word_count']}</word_count>
            </chunk>
"""
                xml_content += """        </chunks>
    </content>
</document>"""
                
                st.download_button(
                    label="Download as XML",
                    data=xml_content,
                    file_name=f"{uploaded_file.name}.xml",
                    mime="application/xml"
                )
            
            # Search functionality
            st.subheader("🔍 Search in Document")
            search_query = st.text_input("Enter search query:")
            
            if search_query and st.session_state.searcher:
                results = st.session_state.searcher.search_chunks(search_query)
                
                if results:
                    st.write(f"Found {len(results)} relevant chunks:")
                    for i, result in enumerate(results):
                        with st.expander(f"Result {i+1} (Score: {result['score']:.2f})"):
                            st.write("**Snippet:**")
                            st.write(result['snippet'])
                            st.write("**Full Chunk:**")
                            st.write(result['chunk']['text'])
                else:
                    st.info("No results found for your search query.")
            
            # Show chunk details
            with st.expander("📊 Chunk Details"):
                for i, chunk in enumerate(chunks):
                    st.write(f"**Chunk {i+1}:**")
                    st.write(f"- Word count: {chunk['word_count']}")
                    st.write(f"- Text preview: {chunk['text'][:100]}...")
                    st.write("---")
        else:
            st.error("Failed to process the document. Please check the file and try again.")

if __name__ == "__main__":
    main()
