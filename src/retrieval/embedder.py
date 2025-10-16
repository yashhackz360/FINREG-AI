import logging
import torch
from sentence_transformers import SentenceTransformer
from typing import List

class Embedder:
    """
    A wrapper class for a SentenceTransformer model to handle text embedding.
    It automatically selects the best available device (CUDA or CPU) for performance.
    """
    def __init__(self, model_name: str):
        self.logger = logging.getLogger(__name__)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Embedder is using device: {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.batch_size = 32  #  <-- ADD THIS LINE to define the attribute
        self.logger.info(f"Successfully loaded embedding model: {model_name}")


    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Encodes a list of texts into a list of vector embeddings.

        Args:
            texts (List[str]): A list of text strings to encode.

        Returns:
            A list of lists, where each inner list is a vector embedding.
        """
        if not texts:
            self.logger.warning("generate_embeddings was called with an empty list of texts.")
            return []

        self.logger.info(f"Generating embeddings for {len(texts)} text documents...")
        try:
            # The model encodes the text, normalizes the embeddings for cosine similarity,
            # and returns them as a list of Python lists.
            embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True  # <-- ADD THIS ARGUMENT
            ).tolist()
            self.logger.info("Embeddings generated successfully.")
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings. Error: {e}", exc_info=True)
            return []

