import hashlib
import pickle
import logging
from pathlib import Path
from typing import Set, Dict, Any

class RSSMonitorState:
    """
    Manages the state of processed RSS feed items to prevent duplicates.
    It works by storing a hash of each processed item's title and link in a file.
    """
    def __init__(self, state_file: str = "artifacts/rss_state.pkl"):
        self.state_file = Path(state_file)
        # Ensure the 'artifacts' directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.seen_items: Set[str] = self._load_state()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loaded {len(self.seen_items)} seen RSS items from state.")

    def _load_state(self) -> Set[str]:
        """Loads the set of seen item hashes from the state file."""
        if not self.state_file.exists():
            return set()
        try:
            with open(self.state_file, 'rb') as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            self.logger.error(f"Could not load state file {self.state_file}, starting fresh. Error: {e}")
            return set()

    def _save_state(self):
        """Saves the current set of seen item hashes to the state file."""
        try:
            with open(self.state_file, 'wb') as f:
                pickle.dump(self.seen_items, f)
        except IOError as e:
            self.logger.error(f"Could not save state to {self.state_file}. Error: {e}")

    # --- NEW METHOD FOR TROUBLESHOOTING ---
    def clear_state(self):
        """Clears the set of seen items and deletes the state file."""
        self.seen_items = set()
        if self.state_file.exists():
            self.state_file.unlink()
        self._save_state()
        self.logger.info("Cleared RSS monitor state.")
    # --- END OF NEW METHOD ---

    def _get_content_hash(self, item: Dict[str, Any]) -> str:
        """Generates a unique MD5 hash for an RSS feed item."""
        # The hash is based on the title and link to identify unique articles.
        content = f"{item.get('title', '')}{item.get('link', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def is_new(self, item: Dict[str, Any]) -> bool:
        """
        Checks if an RSS item is new. If it is, its hash is added to the state.
        Returns True if the item is new, False otherwise.
        """
        if not item or not item.get('link'):
            return False # Ignore items without a link

        item_hash = self._get_content_hash(item)
        if item_hash in self.seen_items:
            return False  # Item has been seen before

        # If new, add to state and save
        self.seen_items.add(item_hash)
        self._save_state()
        return True