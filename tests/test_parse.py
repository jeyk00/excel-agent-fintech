import os
import sys
from src.parser import parse_pdf

def test_parse_pdf_integration():
    """
    Integration test for parse_pdf.
    Requires a valid PDF file at 'data/raw/sample_report.pdf' or passed as argument.
    """
    # Check if a path was provided as an argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Default test path
        pdf_path = "data/raw/sample_report.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"SKIPPING TEST: PDF file not found at {pdf_path}")
        print("Please place a sample PDF at 'data/raw/sample_report.pdf' or provide a path as an argument.")
        return

    print(f"Testing parse_pdf with: {pdf_path}")
    try:
        markdown_content = parse_pdf(pdf_path)
        assert markdown_content is not None
        assert len(markdown_content) > 0
        assert isinstance(markdown_content, str)
        
        print("SUCCESS: PDF parsed successfully.")
        print(f"Output length: {len(markdown_content)} characters.")
        
        # Save output for inspection
        output_path = pdf_path.replace(".pdf", ".md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Markdown saved to: {output_path}")
        
    except Exception as e:
        print(f"FAILURE: Parsing failed with error: {e}")
        raise e

if __name__ == "__main__":
    test_parse_pdf_integration()
