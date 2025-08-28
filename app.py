import streamlit as st
import PyPDF2
import os
from io import BytesIO
from zipfile import ZipFile
import base64
from tempfile import NamedTemporaryFile
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="PDF Master Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
        padding: 1rem;
        background:linear-gradient(90deg,rgba(255, 140, 140, 1) 0%, rgba(240, 98, 96, 1) 100%);
        border-radius: 8px;
        border-bottom: 3px solid #FF4B4B;
    }
    
    /* Card styling */
    .card {
        background-color: #FFCAC9;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #FF4B4B;
        color: #333333;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF4B4B 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 75, 75, 0.3);
    }
    
    /* Secondary button */
    .secondary-btn {
        background: linear-gradient(90deg, #FFCAC9 0%, #FFD5D4 100%) !important;
        border: 1px solid #FFB6B5 !important;
        color: #333333 !important;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background-color: #FFD5D4;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border: 1px solid #FFB6B5;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
        color: #333333;
    }
    
    .uploadedFile:hover {
        background-color: #FFB6B5;
        transform: translateX(5px);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1v0mbdj {
        background-color: #FFCAC9 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #FF4B4B;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: #FFCAC9;
        padding: 1rem;
        border-radius: 8px;
        color: #333333;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #666666;
        font-size: 0.9rem;
        padding: 1rem;
        border-top: 1px solid #FFD5D4;
    }
    
    /* File info cards */
    .file-info {
        background-color: #FFD5D4;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #333333;
    }
    
    /* Success message */
    .success-msg {
        background-color: #D4EDDA;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #28A745;
    }
    
    /* Warning message */
    .warning-msg {
        background-color: #FFF3CD;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #FFC107;
    }
    
    /* Adjust sidebar text color for better contrast */
    .sidebar .sidebar-content {
        color: #333333;
    }
    
    /* Adjust info text in sidebar */
    .stInfo {
        background-color: #FFD5D4 !important;
        color: #333333 !important;
        border-left: 4px solid #FF4B4B !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to create download link for files
def create_download_link(file_data, filename, text):
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="\
        display: inline-block;\
        background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%);\
        color: white;\
        padding: 0.7rem 1.5rem;\
        text-decoration: none;\
        border-radius: 8px;\
        font-weight: 600;\
        margin-top: 1rem;\
        transition: all 0.3s ease;\
        ">{text}</a>'
    return href

# Function to merge PDFs
def merge_pdfs(pdf_files, order):
    merger = PyPDF2.PdfMerger()
    
    # Sort files based on user selection
    if order == "Ascending":
        pdf_files.sort(key=lambda x: x.name)
    elif order == "Descending":
        pdf_files.sort(key=lambda x: x.name, reverse=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf_file in enumerate(pdf_files):
        status_text.text(f"Processing {pdf_file.name}... ({i+1}/{len(pdf_files)})")
        merger.append(pdf_file)
        progress_bar.progress((i + 1) / len(pdf_files))
    
    output_buffer = BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)
    
    status_text.text("Merging complete!")
    progress_bar.progress(100)
    
    return output_buffer

# Function to split PDF
def split_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    zip_buffer = BytesIO()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ZipFile(zip_buffer, 'w') as zip_file:
        for page_num in range(len(pdf_reader.pages)):
            status_text.text(f"Processing page {page_num + 1} of {len(pdf_reader.pages)}...")
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num])
            
            with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                pdf_writer.write(temp_file.name)
                temp_file.seek(0)
                zip_file.write(temp_file.name, f"page_{page_num + 1}.pdf")
            os.unlink(temp_file.name)
            
            progress_bar.progress((page_num + 1) / len(pdf_reader.pages))
    
    zip_buffer.seek(0)
    status_text.text("Splitting complete!")
    progress_bar.progress(100)
    
    return zip_buffer

# Function to display file information
def display_file_info(file):
    file_size = len(file.getvalue()) / 1024  # Size in KB
    upload_time = datetime.now().strftime("%H:%M:%S")
    
    return f"""
    <div class="file-info">
        <strong>Name:</strong> {file.name}<br>
        <strong>Size:</strong> {file_size:.2f} KB<br>
        <strong>Uploaded:</strong> {upload_time}
    </div>
    """

# Main app
def main():
    # Header section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">📄 PDF Master Pro</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #94A3B8; margin-bottom: 2rem;">Professional PDF manipulation tool for merging and splitting documents</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=80)
        st.markdown("### Navigation")
        app_mode = st.radio("Select Operation", ["Merge PDFs", "Split PDF"])
        
        st.markdown("---")
        
        st.markdown("### Recent Activity")
        if 'recent_actions' not in st.session_state:
            st.session_state.recent_actions = []
        
        for action in st.session_state.recent_actions[-5:]:
            st.info(f"• {action}")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        <div style="color: #333333; font-size: 0.9rem;">
        PDF Master Pro allows you to:
        - Merge multiple PDF files into one
        - Split PDFs into individual pages
        - All processing happens in your browser
        - Your files are never uploaded to any server
        </div>
        """, unsafe_allow_html=True)
    
    # Main content based on selection
    if app_mode == "Merge PDFs":
        st.markdown('<div class="card"><h2>Merge PDF Files</h2><p>Combine multiple PDF documents into a single file</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Upload PDF Files")
            uploaded_files = st.file_uploader(
                "Select PDF files to merge", 
                type="pdf", 
                accept_multiple_files=True,
                help="Select multiple PDF files to merge into a single PDF",
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                st.markdown("#### Files to Merge")
                for file in uploaded_files:
                    st.markdown(f'<div class="uploadedFile">📄 {file.name}</div>', unsafe_allow_html=True)
        
        with col2:
            if uploaded_files:
                st.markdown("#### Merge Options")
                order = st.radio("Sort order:", ["As Uploaded", "Ascending", "Descending"], horizontal=True)
                
                # File information
                st.markdown("#### File Details")
                for file in uploaded_files:
                    st.markdown(display_file_info(file), unsafe_allow_html=True)
                
                if st.button("Merge PDFs", key="merge_btn"):
                    if len(uploaded_files) < 2:
                        st.markdown('<div class="warning-msg">Please upload at least 2 PDF files to merge.</div>', unsafe_allow_html=True)
                    else:
                        with st.spinner("Merging your PDFs..."):
                            merged_pdf = merge_pdfs(uploaded_files, order)
                            
                        st.markdown('<div class="success-msg">PDFs merged successfully!</div>', unsafe_allow_html=True)
                        st.session_state.recent_actions.append(f"Merged {len(uploaded_files)} files at {datetime.now().strftime('%H:%M')}")
                        
                        # Download section
                        st.markdown("### Download")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(create_download_link(
                                merged_pdf.getvalue(), 
                                "merged_document.pdf", 
                                "📥 Download Merged PDF"
                            ), unsafe_allow_html=True)
                        with col2:
                            if st.button("Clear Files", key="clear_merge"):
                                st.experimental_rerun()
            else:
                st.markdown("""
                <div style="background-color: #FFCAC9; padding: 2rem; border-radius: 12px; text-align: center; color: #333333;">
                    <h3>No Files Selected</h3>
                    <p>Upload PDF files to begin merging</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:  # Split PDF mode
        st.markdown('<div class="card"><h2>Split PDF File</h2><p>Extract individual pages from a PDF document</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Upload PDF File")
            uploaded_file = st.file_uploader(
                "Select a PDF file to split", 
                type="pdf",
                help="Select a multi-page PDF file to split into individual pages",
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                st.markdown("#### File to Split")
                st.markdown(f'<div class="uploadedFile">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
        
        with col2:
            if uploaded_file:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                num_pages = len(pdf_reader.pages)
                
                st.markdown("#### Document Information")
                st.markdown(f"""
                <div class="file-info">
                    <strong>Name:</strong> {uploaded_file.name}<br>
                    <strong>Pages:</strong> {num_pages}<br>
                    <strong>Size:</strong> {len(uploaded_file.getvalue()) / 1024:.2f} KB
                </div>
                """, unsafe_allow_html=True)
                
                if num_pages > 1:
                    st.markdown(f"#### Split Options")
                    st.info(f"This PDF contains {num_pages} pages. Each page will be extracted as a separate PDF file.")
                    
                    if st.button("Split PDF", key="split_btn"):
                        with st.spinner("Splitting your PDF into individual pages..."):
                            zip_buffer = split_pdf(uploaded_file)
                            
                        st.markdown('<div class="success-msg">PDF split successfully!</div>', unsafe_allow_html=True)
                        st.session_state.recent_actions.append(f"Split {uploaded_file.name} ({num_pages} pages) at {datetime.now().strftime('%H:%M')}")
                        
                        # Download section
                        st.markdown("### Download")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(create_download_link(
                                zip_buffer.getvalue(), 
                                "split_pages.zip", 
                                "📥 Download Split Pages (ZIP)"
                            ), unsafe_allow_html=True)
                        with col2:
                            if st.button("Clear File", key="clear_split"):
                                st.experimental_rerun()
                else:
                    st.markdown('<div class="warning-msg">This PDF already has only one page. Splitting is not needed.</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #FFCAC9; padding: 2rem; border-radius: 12px; text-align: center; color: #333333;">
                    <h3>No File Selected</h3>
                    <p>Upload a PDF file to begin splitting</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>PDF Master Pro • Secure PDF Processing • v2.0</p>
        <p>All rights reserved © 2023</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
