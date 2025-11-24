import os
import nest_asyncio
from llama_parse import LlamaParse
from dotenv import load_dotenv

# Apply nest_asyncio to allow nested event loops (common in Jupyter/some envs)
nest_asyncio.apply()

load_dotenv()

def parse_pdf(file_path: str) -> str:
    """
    Parses a PDF file using LlamaParse and returns the content as Markdown.
    
    Args:
        file_path (str): Path to the PDF file.
        
    Returns:
        str: The parsed content in Markdown format.
    """
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Parsing PDF: {file_path}...")
    
    parser = LlamaParse(
        result_type="markdown",
        api_key=api_key,
        verbose=True,
        language="en" # Default to English, but can be changed or made dynamic if needed. 
                      # For Polish reports, we might want to check if 'pl' is supported or if 'en' works well enough (usually does for layout).
                      # LlamaParse is quite good at multi-lingual.
    )
    
    # load_data returns a list of Document objects
    documents = parser.load_data(file_path)
    
    # Combine text from all pages/documents
    full_text = "\n\n".join([doc.text for doc in documents])
    
    return full_text

if __name__ == "__main__":
    # Simple test block
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        try:
            markdown_output = parse_pdf(pdf_path)
            print("--- Parsed Output Start ---")
            print(markdown_output[:500] + "\n... (truncated)")
            print("--- Parsed Output End ---")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python src/parser.py <path_to_pdf>")
