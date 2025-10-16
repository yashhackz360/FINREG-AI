import logging
import requests
import hashlib
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Tuple
from src.processing.document_processor import DocumentProcessor

class RealTimeDocumentProcessor(DocumentProcessor):
    """
    Extends the base DocumentProcessor to handle real-time updates from a stream.
    It is responsible for fetching web content, cleaning it, and chunking it.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _fetch_content(self, url: str) -> str:
        """Fetches HTML content from a given URL."""
        try:
            response = requests.get(url, timeout=20, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch content from {url}. Error: {e}")
            return ""

    def _extract_text(self, html: str) -> str:
        """Extracts and cleans the main text content from raw HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        # Remove common non-content tags to clean up the text
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        # Get text, using a space as a separator, and strip excess whitespace
        return soup.get_text(separator=' ', strip=True)

    def process_update(self, update: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
        """
        Processes a single update from the Kafka stream.

        Args:
            update (Dict[str, Any]): A dictionary representing the message from Kafka.
                                     Expected to contain a 'url' key.

        Returns:
            A tuple containing (list of formatted chunks, full cleaned text).
        """
        url = update.get('url')
        if not url:
            self.logger.warning("Received an update with no URL.")
            return [], ""
        
        self.logger.info(f"Processing update for URL: {url}")
        html_content = self._fetch_content(url)
        if not html_content:
            return [], ""

        cleaned_text = self._extract_text(html_content)
        text_chunks = self.chunk_text(cleaned_text)
        
        # Use a hash of the URL to create a consistent document ID
        doc_id = hashlib.md5(url.encode()).hexdigest()
        
        # Format the chunks with consistent metadata for the vector database
        processed_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_metadata = {**update, 'text': chunk_text}
            processed_chunks.append({
                'id': f"{doc_id}_{i}", # Create a unique ID for each chunk
                'text': chunk_text,
                'metadata': chunk_metadata
            })
            
        self.logger.info(f"Successfully processed and chunked URL into {len(processed_chunks)} chunks.")
        return processed_chunks, cleaned_text

