import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from src.filter import filter_financial_pages
from src.parser import parse_pdf
from src.extractor import extract_data
from src.analyzer import analyze_report
from src.reporter import generate_excel_report

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Page Config
st.set_page_config(page_title="AI Financial Analyst", page_icon="💸", layout="wide")

# Title and Header
st.title("💸 AI Financial Analyst Agent")
st.markdown("""
**Upload a PDF financial report** (e.g., Annual Report) and let the AI extract key metrics, 
calculate EBITDA, and generate an investor-grade Excel dashboard.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox(
        "Select Model",
        ["gemini-2.0-flash", "gpt-4o", "deepseek-reasoner"],
        index=0
    )
    use_filter = st.checkbox("Use Smart PDF Filter", value=True, help="Reduces cost and noise by filtering relevant pages.")
    
    st.divider()
    st.info("Ensure API Keys are set in `.env`.")

# File Uploader
uploaded_file = st.file_uploader("Upload Annual Report (PDF)", type="pdf")

if uploaded_file and st.button("🚀 Start Analysis"):
    # Initialize Progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create directories if not exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    try:
        # 1. Save File
        status_text.text("📥 Saving uploaded file...")
        input_path = os.path.join("data", "raw", uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        progress_bar.progress(10)
        
        # 2. Filter PDF
        pdf_to_process = input_path
        if use_filter:
            status_text.text("🔍 Smart Filtering: Scanning for financial pages...")
            filtered_path = os.path.join("data", "temp", f"filtered_{uploaded_file.name}")
            if filter_financial_pages(input_path, filtered_path):
                pdf_to_process = filtered_path
                st.success(f"Smart Filter: Reduced PDF to relevant pages.")
            else:
                st.warning("Smart Filter found no matches. Using original PDF.")
        progress_bar.progress(30)
        
        # 3. Parse PDF
        status_text.text("📄 Parsing PDF to Markdown (LlamaParse)...")
        markdown_text = parse_pdf(pdf_to_process)
        progress_bar.progress(50)
        
        # 4. Extract Data
        status_text.text(f"🤖 Extracting data with {model_name}...")
        report = extract_data(markdown_text, model_name=model_name)
        progress_bar.progress(70)
        
        # 5. Analyze Data
        status_text.text("📊 Calculating KPIs (EBITDA, Margins, Growth)...")
        df = analyze_report(report)
        
        # Display Raw Data Preview
        with st.expander("Show Raw Data Preview"):
            st.dataframe(df)
            
        progress_bar.progress(85)
        
        # 6. Generate Report
        status_text.text("📈 Generating Investor-Grade Excel Dashboard...")
        output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.xlsx"
        output_path = os.path.join("data", "processed", output_filename)
        
        final_path = generate_excel_report(df, output_path)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis Complete!")
        
        st.success(f"Report generated successfully!")
        
        # 7. Download Button
        if final_path and os.path.exists(final_path):
            with open(final_path, "rb") as f:
                st.download_button(
                    label="📥 Download Excel Dashboard",
                    data=f,
                    file_name=os.path.basename(final_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # print full traceback to console for debugging
        import traceback
        traceback.print_exc()
