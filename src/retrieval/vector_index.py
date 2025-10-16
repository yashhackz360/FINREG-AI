import logging
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from src.config import PineconeConfig

class VectorIndex:
    """
    Manages all interactions with a Pinecone vector index, including
    initialization, creation, upserting data, and querying.
    """
    def __init__(self, config: PineconeConfig):
        """
        Initializes the connection to Pinecone and ensures the specified index exists.

        Args:
            config (PineconeConfig): A dataclass containing Pinecone API key,
                                     index name, and configuration.
        """
        self.logger = logging.getLogger(__name__)
        self.pc = Pinecone(api_key=config.api_key)
        self.index_name = config.index_name
        
        # Check if the index already exists. If not, create it.
        if self.index_name not in self.pc.list_indexes().names():
            self.logger.warning(f"Index '{self.index_name}' not found. Creating a new one...")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric=config.metric,
                # Using serverless spec for pay-as-you-go pricing, suitable for academic projects
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            self.logger.info(f"Index '{self.index_name}' created successfully.")
        else:
            self.logger.info(f"Successfully connected to existing index '{self.index_name}'.")
            
        self.index = self.pc.Index(self.index_name)

    def upsert_vectors(self, vectors: List[Dict[str, Any]], batch_size: int = 100):
        """
        Upserts (inserts or updates) data into the Pinecone index in batches.

        Args:
            vectors (List[Dict[str, Any]]): A list of vectors to upsert. Each dict
                                             should have 'id', 'values', and 'metadata'.
            batch_size (int): The number of vectors to upsert in each API call.
        """
        if not vectors:
            self.logger.warning("upsert_vectors called with an empty list.")
            return
            
        self.logger.info(f"Upserting {len(vectors)} vectors in batches of {batch_size}...")
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
            except Exception as e:
                self.logger.error(f"Failed to upsert batch. Error: {e}", exc_info=True)
        self.logger.info("Upsert operation completed.")

    def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the index to find the most similar vectors to a given vector.

        Args:
            vector (List[float]): The query vector.
            top_k (int): The number of top results to retrieve.

        Returns:
            A list of matching documents, formatted as dictionaries.
        """
        try:
            results = self.index.query(
                vector=vector, 
                top_k=top_k, 
                include_metadata=True
            )
            # Convert Pinecone's match objects to a more usable dictionary format
            return [m.to_dict() for m in results.get('matches', [])]
        except Exception as e:
            self.logger.error(f"Failed to query index. Error: {e}", exc_info=True)
            return []

