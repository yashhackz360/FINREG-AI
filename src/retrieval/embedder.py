import logging
from typing import List

try:
    import torch
    from sentence_transformers import SentenceTransformer
except ImportError:  # lightweight deploy: ONNX fastembed, same MiniLM model/vectors
    torch = None
    SentenceTransformer = None


class Embedder:
    """
    Wrapper for text embedding. Uses sentence-transformers when installed,
    otherwise falls back to fastembed (ONNX, low memory) with the same model.
    """
    def __init__(self, model_name: str):
        self.logger = logging.getLogger(__name__)
        self.batch_size = 32
        self._lite = SentenceTransformer is None
        if self._lite:
            from fastembed import TextEmbedding
            self.model = TextEmbedding(model_name)
            self.logger.info(f"Loaded fastembed model: {model_name}")
            return
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Embedder is using device: {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.logger.info(f"Successfully loaded embedding model: {model_name}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Encodes a list of texts into a list of vector embeddings."""
        if not texts:
            self.logger.warning("generate_embeddings was called with an empty list of texts.")
            return []
        try:
            if self._lite:
                return [e.tolist() for e in self.model.embed(texts)]
            return self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
            ).tolist()
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings. Error: {e}", exc_info=True)
            return []
