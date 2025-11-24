import os
from pypdf import PdfReader, PdfWriter

# Keyword scoring configuration
KEYWORDS = {
    "skonsolidowane sprawozdanie": 50,    # Target: Consolidated reports
    "rachunek zysków i strat": 100,       # Target: P&L
    "sytuacji finansowej": 100,           # Target: Balance Sheet
    "przepływy pieniężne": 100,           # Target: Cash Flow
    "aktywa": 20,                         # Validation keyword
    "pasywa": 20,                         # Validation keyword
    "przychody ze sprzedaży": 20,         # Validation keyword
    "zysk netto": 20,                     # Validation keyword
}

NEGATIVE_KEYWORDS = {
    "spis treści": -500,                  # Skip Table of Contents
    "strona": -5,                         # Minor penalty for footers to avoid empty pages
}

def filter_financial_pages(input_path: str, output_path: str, threshold: int = 50) -> bool:
    """
    Scans a PDF and creates a new PDF containing only pages that match specific financial keywords.
    
    Args:
        input_path (str): Path to the source PDF.
        output_path (str): Path to save the filtered PDF.
        threshold (int): Minimum score required to include a page.
        
    Returns:
        bool: True if pages were found and saved, False otherwise.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    pages_kept = 0
    total_pages = len(reader.pages)
    
    print(f"🔍 Scanning {total_pages} pages in {os.path.basename(input_path)}...")
    
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text().lower()
            if not text:
                continue
                
            score = 0
            
            # Calculate score
            for keyword, points in KEYWORDS.items():
                if keyword in text:
                    score += points
                    
            for keyword, points in NEGATIVE_KEYWORDS.items():
                if keyword in text:
                    score += points
            
            # Decision
            if score > threshold:
                writer.add_page(page)
                pages_kept += 1
                print(f"  ✅ Page {i+1}: Score {score} (Kept)")
            # else:
            #     print(f"  ❌ Page {i+1}: Score {score} (Dropped)")
                
        except Exception as e:
            print(f"  ⚠️ Error reading page {i+1}: {e}")
            continue
            
    if pages_kept > 0:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        print(f"✨ Created filtered PDF: {output_path}")
        print(f"📊 Stats: Kept {pages_kept}/{total_pages} pages ({pages_kept/total_pages:.1%})")
        return True
    else:
        print("⚠️ No relevant pages found. Threshold might be too high or PDF is image-based.")
        return False

if __name__ == "__main__":
    # Test block
    import sys
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
        output_pdf = os.path.join("data", "temp", "filtered_report.pdf")
        filter_financial_pages(input_pdf, output_pdf)
    else:
        print("Usage: python src/filter.py <input_pdf>")
