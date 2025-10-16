import json
import os
import logging
from typing import List

class StateManager:
    """
    A generic state manager for tracking processed URLs from any source.
    This is useful for scrapers or other ingestion methods that are not RSS-based.
    It stores a simple list of URLs in a JSON file.
    """
    def __init__(self, state_file_path: str = "artifacts/processed_urls.json"):
        self.state_file_path = state_file_path
        # Ensure the 'artifacts' directory exists
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)
        self.processed_urls: List[str] = self._load_state()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loaded {len(self.processed_urls)} processed URLs from state file.")

    def _load_state(self) -> List[str]:
        """Loads the list of URLs from the JSON state file."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.error(f"Could not decode JSON from {self.state_file_path}. Starting with an empty state.")
                return []
        return []

    def _save_state(self):
        """Saves the current list of URLs to the JSON state file."""
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump(self.processed_urls, f, indent=4)
        except IOError as e:
            self.logger.error(f"Could not save state to {self.state_file_path}. Error: {e}")

    def add_processed_urls(self, urls: List[str]):
        """Adds a list of new URLs to the state."""
        new_urls_added = False
        for url in urls:
            if url not in self.processed_urls:
                self.processed_urls.append(url)
                new_urls_added = True

        if new_urls_added:
            self._save_state()
            self.logger.info(f"Added {len(urls)} new URLs to state. Total is now {len(self.processed_urls)}.")


    def filter_new_urls(self, urls: List[str]) -> List[str]:
        """Filters a list of URLs, returning only the ones not yet processed."""
        return [url for url in urls if url not in self.processed_urls]

