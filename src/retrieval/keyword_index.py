import pickle
import logging
from pathlib import Path
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

class KeywordIndex:
    """Manages the creation, saving, and loading of a BM25 keyword index."""
    def __init__(self, index_path: str = "artifacts/bm25_index.pkl"):
        self.index_path = Path(index_path)
        self.logger = logging.getLogger(__name__)
        # NOTE: We no longer load the index at initialization to prevent stale reads.

    def _load_from_disk(self):
        """Loads the BM25 index and documents from the pickle file."""
        if self.index_path.exists():
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    return data.get('documents', []), data.get('index', None)
            except (pickle.UnpicklingError, EOFError) as e:
                self.logger.error(f"Could not read BM25 index file, it may be corrupted or empty: {e}")
                return [], None
        return [], None

    def _save_to_disk(self, documents: List[Dict[str, Any]], bm25_index):
        """Saves the index and documents to a pickle file."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump({'documents': documents, 'index': bm25_index}, f)

    def update_index(self, new_docs: List[Dict[str, Any]]):
        """Adds new documents to the index and retrains it."""
        if not new_docs:
            return

        documents, _ = self._load_from_disk()
        # Prevent adding duplicate documents
        existing_ids = {doc['id'] for doc in documents}
        unique_new_docs = [doc for doc in new_docs if doc['id'] not in existing_ids]
        
        if not unique_new_docs:
            return

        documents.extend(unique_new_docs)
        
        tokenized_corpus = [doc['text'].lower().split(" ") for doc in documents]
        bm25_index = BM25Okapi(tokenized_corpus)
        
        self._save_to_disk(documents, bm25_index)
        self.logger.info(f"Updated and saved BM25 index. Total documents: {len(documents)}")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a keyword search by loading the latest index from disk.
        """
        documents, bm25_index = self._load_from_disk()
        
        if not bm25_index or not documents:
            self.logger.warning("BM25 index file not found or is empty. Cannot perform search.")
            return []
        
        tokenized_query = query.lower().split(" ")
        doc_scores = bm25_index.get_scores(tokenized_query)
        
        top_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]
        return [documents[i] for i in top_indices]

