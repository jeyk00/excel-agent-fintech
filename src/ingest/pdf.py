import os
import nest_asyncio
from llama_parse import LlamaParse
from dotenv import load_dotenv
from src.ingest.base import IngestionStrategy

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

load_dotenv()

class PDFIngestionStrategy(IngestionStrategy):
    """
    Ingestion strategy for PDF files using LlamaParse.
    """
    
    def parse(self, file_path: str) -> str:
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
            language="en" 
        )
        
        # load_data returns a list of Document objects
        documents = parser.load_data(file_path)
        
        # Combine text from all pages/documents
        full_text = "\n\n".join([doc.text for doc in documents])
        
        return full_text
