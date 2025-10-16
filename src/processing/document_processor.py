import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

class DocumentProcessor:
    """
    Handles the splitting of large texts into smaller, manageable chunks.
    This class uses a recursive character text splitter for intelligent chunking.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Initializes the DocumentProcessor with specific chunking parameters.

        Args:
            chunk_size (int): The maximum size of each text chunk (in characters).
            chunk_overlap (int): The number of characters to overlap between chunks
                                 to maintain context.
        """
        self.logger = logging.getLogger(__name__)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            # These separators try to split on the most logical boundaries first.
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.logger.info(f"DocumentProcessor initialized with chunk_size={chunk_size} and chunk_overlap={chunk_overlap}.")

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits a given text into a list of smaller chunks.

        Args:
            text (str): The large block of text to be chunked.

        Returns:
            A list of strings, where each string is a text chunk.
        """
        if not text:
            self.logger.warning("chunk_text was called with empty or None text.")
            return []
            
        chunks = self.text_splitter.split_text(text)
        self.logger.info(f"Successfully split text into {len(chunks)} chunks.")
        return chunks

