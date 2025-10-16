import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional

class WebIngestor:
    """
    A stub for a generic web ingestion tool.
    
    This component would be responsible for fetching the full content of a webpage
    from a given URL and extracting the primary article text, cleaning it of
    HTML tags, navigation menus, ads, and other boilerplate.
    
    A full implementation would likely use more advanced libraries like 
    Newspaper3k or a custom-trained model for content extraction.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def ingest(self, url: str) -> Optional[Dict[str, str]]:
        """
        Fetches and extracts content from a URL.
        
        Args:
            url (str): The URL of the webpage to process.
            
        Returns:
            A dictionary containing the title and cleaned content, or None on failure.
        """
        self.logger.info(f"Attempting to ingest content from: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Placeholder for content extraction logic ---
            # A simple approach is to find the main content tag, but this is unreliable.
            # For example, one might look for <article> or <main> tags.
            # This stub will just extract all text for demonstration.
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get title
            title = soup.title.string if soup.title else "No Title Found"

            self.logger.info(f"Successfully ingested and cleaned content from {url}")
            return {
                "title": title,
                "content": cleaned_text,
                "url": url
            }

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch content from {url}. Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during ingestion of {url}. Error: {e}")
            return None

