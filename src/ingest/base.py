from abc import ABC, abstractmethod

class IngestionStrategy(ABC):
    """
    Abstract base class for file ingestion strategies.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        Parses a file and returns its content as a string (Markdown preferred).
        
        Args:
            file_path (str): Path to the file to parse.
            
        Returns:
            str: Parsed content.
        """
        pass
