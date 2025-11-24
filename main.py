import os
import sys
import argparse
from dotenv import load_dotenv

from src.parser import parse_pdf
from src.extractor import extract_data
from src.analyzer import analyze_report
from src.reporter import generate_excel_report
from src.filter import filter_financial_pages

# Load environment variables
load_dotenv()

# Force UTF-8 encoding for stdout (Windows fix)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Financial Agent E2E - PDF to Excel Converter")
    parser.add_argument("pdf_path", help="Path to the input PDF financial report")
    parser.add_argument("--output", "-o", help="Path to the output Excel file (default: processed/<pdf_name>.xlsx)")
    parser.add_argument("--model", "-m", default="gemini-2.0-flash", help="LLM model to use (default: gemini-2.0-flash)")
    parser.add_argument("--no-filter", action="store_true", help="Disable Smart PDF Filtering")
    
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
        
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Default to data/processed/filename.xlsx
        base_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_path = os.path.join("data", "processed", f"{name_without_ext}.xlsx")
        
    print(f"🚀 Starting Financial Agent...")
    print(f"📂 Input: {pdf_path}")
    print(f"🤖 Model: {args.model}")
    
    # 0. Smart Filter
    parsing_path = pdf_path
    if not args.no_filter:
        print("\n[0/4] Running Smart PDF Filter...")
        filtered_path = os.path.join("data", "temp", f"filtered_{os.path.basename(pdf_path)}")
        try:
            if filter_financial_pages(pdf_path, filtered_path):
                parsing_path = filtered_path
                print(f"✅ Using filtered PDF: {parsing_path}")
            else:
                print("⚠️ Filter found no pages (or failed). Using original PDF.")
        except Exception as e:
            print(f"⚠️ Filter failed: {e}. Using original PDF.")
    else:
        print("\n[0/4] Skipping Smart Filter (user requested).")

    # 1. Parse PDF
    print(f"\n[1/4] Parsing PDF ({os.path.basename(parsing_path)}) with LlamaParse...")
    try:
        markdown_text = parse_pdf(parsing_path)
        print(f"✅ Parsed {len(markdown_text)} characters.")
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        sys.exit(1)
        
    # 2. Extract Data
    print("\n[2/4] Extracting data with LLM...")
    try:
        report = extract_data(markdown_text, model_name=args.model)
        print(f"✅ Extracted data for {report.company_name} ({len(report.periods)} periods).")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)
        
    # 3. Analyze Data
    print("\n[3/4] Analyzing and transforming data...")
    try:
        df = analyze_report(report)
        print(f"✅ Calculated KPIs. DataFrame shape: {df.shape}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)
        
    # 4. Generate Report
    print("\n[4/4] Generating Excel report...")
    try:
        generate_excel_report(df, output_path)
        print(f"✅ Report saved to: {output_path}")
    except Exception as e:
        print(f"❌ Reporting failed: {e}")
        sys.exit(1)
        
    print("\n✨ Process completed successfully!")

if __name__ == "__main__":
    main()
