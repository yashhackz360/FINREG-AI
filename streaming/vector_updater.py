import logging
from typing import List, Dict, Any
from src.retrieval.vector_index import VectorIndex
from src.retrieval.embedder import Embedder

class RealTimeVectorUpdater:
    """
    Handles the final step of the ingestion pipeline: generating embeddings
    for new text chunks and upserting them into the vector database.
    """
    def __init__(self, vector_index: VectorIndex, embedder: Embedder):
        """
        Initializes the updater with its necessary components.

        Args:
            vector_index (VectorIndex): An instance of the vector index manager.
            embedder (Embedder): An instance of the text embedder.
        """
        self.vector_index = vector_index
        self.embedder = embedder
        self.logger = logging.getLogger(__name__)
        self.logger.info("RealTimeVectorUpdater initialized.")

    def update_vectors(self, chunks: List[Dict[str, Any]]):
        """
        Processes a list of chunks to generate embeddings and upsert them.

        Args:
            chunks (List[Dict[str, Any]]): A list of processed chunks, each
                                           containing an 'id', 'text', and 'metadata'.
        """
        if not chunks:
            self.logger.info("No chunks provided to update, skipping.")
            return

        self.logger.info(f"Updating vectors for {len(chunks)} new chunks.")
        
        # Extract the text content from each chunk to be embedded
        texts_to_embed = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings for all text chunks in a single batch call
        embeddings = self.embedder.generate_embeddings(texts_to_embed)
        
        if not embeddings or len(embeddings) != len(chunks):
            self.logger.error("Mismatch between number of chunks and generated embeddings. Aborting update.")
            return
            
        # Prepare the data in the format required by the Pinecone API
        # Prepare the data in the format required by the Pinecone API
        vectors_to_upsert = []
        for chunk, embedding in zip(chunks, embeddings):
            # IMPORTANT: Add the chunk's text into the metadata payload
            metadata = chunk['metadata']
            metadata['text'] = chunk['text'] 
            
            vectors_to_upsert.append({
                'id': chunk['id'],
                'values': embedding,
                'metadata': metadata
            })

        # Upsert the new vectors into the Pinecone index
        self.vector_index.upsert_vectors(vectors_to_upsert)
        self.logger.info(f"Successfully upserted {len(vectors_to_upsert)} vectors into the index.")

