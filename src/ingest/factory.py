import os
from src.ingest.base import IngestionStrategy
from src.ingest.pdf import PDFIngestionStrategy
from src.ingest.xml import XMLIngestionStrategy

def get_ingestion_strategy(file_path: str) -> IngestionStrategy:
    """
    Returns the appropriate ingestion strategy based on the file extension.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        IngestionStrategy: The selected strategy.
        
    Raises:
        ValueError: If the file format is not supported.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return PDFIngestionStrategy()
    elif ext in ['.xml', '.xhtml']:
        return XMLIngestionStrategy()
    else:
        raise ValueError(f"Unsupported file format: {ext}")
