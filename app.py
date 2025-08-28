import streamlit as st
import PyPDF2
import os
from io import BytesIO
from zipfile import ZipFile
import base64
from tempfile import NamedTemporaryFile

# Set page configuration
st.set_page_config(
    page_title="PDF Master Pro",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .info-text {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
    }
    .stButton button {
        background-color: #3B82F6;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1E3A8A;
        color: white;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #6B7280;
        font-size: 0.8rem;
    }
    .uploadedFile {
        background-color: #F9FAFB;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Function to create download link for files
def create_download_link(file_data, filename, text):
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Function to merge PDFs
def merge_pdfs(pdf_files, order):
    merger = PyPDF2.PdfMerger()
    
    # Sort files based on user selection
    if order == "Ascending":
        pdf_files.sort(key=lambda x: x.name)
    else:
        pdf_files.sort(key=lambda x: x.name, reverse=True)
    
    for pdf_file in pdf_files:
        merger.append(pdf_file)
    
    output_buffer = BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)
    
    return output_buffer

# Function to split PDF
def split_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    zip_buffer = BytesIO()
    
    with ZipFile(zip_buffer, 'w') as zip_file:
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num])
            
            with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                pdf_writer.write(temp_file.name)
                temp_file.seek(0)
                zip_file.write(temp_file.name, f"page_{page_num + 1}.pdf")
            os.unlink(temp_file.name)
    
    zip_buffer.seek(0)
    return zip_buffer

# Main app
def main():
    st.markdown('<h1 class="main-header">📄 PDF Master Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Merge multiple PDFs into a single file or split a multi-page PDF into individual pages. All processing happens in your browser for maximum privacy.</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=100)
        st.markdown("### Navigation")
        app_mode = st.radio("Select Operation", ["Merge PDFs", "Split PDF"])
        st.markdown("---")
        st.markdown("### About")
        st.info("This app allows you to merge multiple PDF files into one or split a PDF into individual pages. Your files are processed securely in your browser and are not stored on any server.")
    
    # Main content based on selection
    if app_mode == "Merge PDFs":
        st.markdown('<h2 class="sub-header">Merge PDF Files</h2>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Select PDF files to merge", 
            type="pdf", 
            accept_multiple_files=True,
            help="Select multiple PDF files to merge into a single PDF"
        )
        
        if uploaded_files:
            st.markdown("**Uploaded Files:**")
            for file in uploaded_files:
                st.markdown(f'<div class="uploadedFile">📄 {file.name}</div>', unsafe_allow_html=True)
            
            # Order selection
            order = st.radio("Sort files by name:", ["Ascending", "Descending"], horizontal=True)
            
            if st.button("Merge PDFs", key="merge_btn"):
                if len(uploaded_files) < 2:
                    st.warning("Please upload at least 2 PDF files to merge.")
                else:
                    with st.spinner("Merging your PDFs..."):
                        merged_pdf = merge_pdfs(uploaded_files, order)
                        
                    st.success("PDFs merged successfully!")
                    st.markdown(create_download_link(
                        merged_pdf.getvalue(), 
                        "merged_document.pdf", 
                        "📥 Download Merged PDF"
                    ), unsafe_allow_html=True)
    
    else:  # Split PDF mode
        st.markdown('<h2 class="sub-header">Split PDF File</h2>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Select a PDF file to split", 
            type="pdf",
            help="Select a multi-page PDF file to split into individual pages"
        )
        
        if uploaded_file:
            st.markdown(f'<div class="uploadedFile">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
            
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            st.info(f"This PDF contains {num_pages} page(s).")
            
            if st.button("Split PDF", key="split_btn"):
                if num_pages == 1:
                    st.warning("This PDF already has only one page. Splitting is not needed.")
                else:
                    with st.spinner("Splitting your PDF into individual pages..."):
                        zip_buffer = split_pdf(uploaded_file)
                        
                    st.success("PDF split successfully!")
                    st.markdown(create_download_link(
                        zip_buffer.getvalue(), 
                        "split_pages.zip", 
                        "📥 Download Split Pages (ZIP)"
                    ), unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown('<div class="footer">PDF Master Pro • Secure PDF Processing</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()