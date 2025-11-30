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
from src.ingest.factory import get_ingestion_strategy
from src.extractor import extract_data
from src.analyzer import FinancialAnalyzer
from src.reporter import generate_excel_report
from src.ml.forecaster import RevenueForecaster

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Page Config
st.set_page_config(page_title="AI Financial Analyst v2.0", page_icon="💸", layout="wide")

# Title and Header
st.title("💸 AI Financial Analyst Agent v2.0")
st.markdown("""
**Upload financial reports** (PDF, XML) and let the AI extract key metrics, 
perform multi-year analysis, and forecast future revenue.
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
    st.header("DCF Assumptions")
    wacc = st.slider("WACC (%)", min_value=5.0, max_value=15.0, value=10.0, step=0.5)
    terminal_growth = st.number_input("Terminal Growth Rate (%)", min_value=0.0, max_value=5.0, value=2.5, step=0.1)
    
    st.divider()
    st.info("Ensure API Keys are set in `.env`.")

# File Uploader
uploaded_files = st.file_uploader("Upload Financial Reports", type=["pdf", "xml", "xhtml"], accept_multiple_files=True)

# Initialize Session State
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'forecast_df' not in st.session_state:
    st.session_state.forecast_df = None
if 'final_path' not in st.session_state:
    st.session_state.final_path = None

if uploaded_files and st.button("🚀 Start Analysis"):
    # Initialize Progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create directories if not exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    all_reports = []
    
    try:
        total_files = len(uploaded_files)
        step_size = 100 / (total_files * 4 + 2) # Approximate steps
        current_progress = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            # 1. Save File
            status_text.text(f"📥 Processing {uploaded_file.name}: Saving...")
            input_path = os.path.join("data", "raw", uploaded_file.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 2. Ingestion Strategy
            status_text.text(f"📄 Processing {uploaded_file.name}: Parsing...")
            strategy = get_ingestion_strategy(input_path)
            
            # Special handling for PDF filtering (only if it's a PDF)
            file_to_parse = input_path
            if input_path.lower().endswith('.pdf') and use_filter:
                status_text.text(f"🔍 Processing {uploaded_file.name}: Smart Filtering...")
                filtered_path = os.path.join("data", "temp", f"filtered_{uploaded_file.name}")
                if filter_financial_pages(input_path, filtered_path):
                    file_to_parse = filtered_path
            
            # Parse
            markdown_text = strategy.parse(file_to_parse)
            
            # 3. Extract Data
            status_text.text(f"🤖 Processing {uploaded_file.name}: Extracting data...")
            report = extract_data(markdown_text, model_name=model_name)
            all_reports.append(report)
            
            current_progress += step_size * 4
            progress_bar.progress(min(int(current_progress), 90))
            
            # 4. Aggregation
            status_text.text("📊 Aggregating Reports...")
            analyzer = FinancialAnalyzer(all_reports)
            analyzer.aggregate_data()
            df = analyzer.calculate_metrics()
            
            if not df.empty:
                # 5. Forecasting
                status_text.text("🔮 Forecasting Future Revenue...")
                forecaster = RevenueForecaster(years_ahead=5)
                forecaster.fit(df[['Year', 'revenue']])
                forecast_df = forecaster.predict()
                
                # 6. Generate Report
                status_text.text("📈 Generating Investor-Grade Excel Dashboard...")
                # Use the name of the first file for the output, or a generic name
                base_name = os.path.splitext(uploaded_files[0].name)[0] if uploaded_files else "report"
                output_filename = f"{base_name}_analysis.xlsx"
                output_path = os.path.join("data", "processed", output_filename)
                
                # Merge Forecast into Main DataFrame for the Report
                combined_df = analyzer.enrich_with_forecast(forecast_df)
                
                # Add DCF assumptions to company_info implicitly by passing them to generate_excel_report
                # We need to update generate_excel_report signature first.
                # For now, let's pass them as a dictionary if possible, or update the function.
                
                final_path = generate_excel_report(combined_df, output_path, wacc=wacc/100, terminal_growth=terminal_growth/100)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis Complete!")
            
            # Store results in Session State
            st.session_state.df = df
            st.session_state.forecast_df = forecast_df
            st.session_state.final_path = final_path
            st.session_state.analysis_complete = True
            
        else:
            st.warning("No data extracted from the provided files.")
            progress_bar.progress(100)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # print full traceback to console for debugging
        import traceback
        traceback.print_exc()

# Display Results if Analysis is Complete
if st.session_state.analysis_complete:
    st.success(f"Report generated successfully!")
    
    # Display Raw Data Preview
    if st.session_state.df is not None:
        st.subheader("Historical Data")
        st.dataframe(st.session_state.df)
    
    if st.session_state.forecast_df is not None:
        st.subheader("Revenue Forecast")
        st.line_chart(st.session_state.forecast_df.set_index('Year')['revenue'])
    
    # Download Button
    if st.session_state.final_path and os.path.exists(st.session_state.final_path):
        with open(st.session_state.final_path, "rb") as f:
            st.download_button(
                label="📥 Download Excel Dashboard",
                data=f,
                file_name=os.path.basename(st.session_state.final_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

