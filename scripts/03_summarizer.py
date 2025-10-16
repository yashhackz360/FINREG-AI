import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

from src.config import Config
from src.retrieval.embedder import Embedder
from src.retrieval.vector_index import VectorIndex
from src.generation.llm_generator import LLMGenerator
from streaming.kafka_consumer import RegulatoryDataConsumer

# Configure logging for this specific service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [SummarizerService] - %(message)s'
)

class SummarizationPipeline:
    """
    A pipeline that listens for processed documents, generates summaries,
    and saves them for the UI to display.
    """
    def __init__(self, config: Config):
        self.config = config
        self.embedder = Embedder(config.embedding_model)
        self.vector_index = VectorIndex(config.pinecone_config)
        self.llm_generator = LLMGenerator(config.groq_api_key, config.llm_model)
        self.summaries_path = Path(config.summaries_file_path)
        # Ensure the 'artifacts' directory exists
        self.summaries_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Summarization Pipeline initialized successfully.")

    def _load_summaries(self) -> List[Dict[str, Any]]:
        """Loads the current list of summaries from the JSON file."""
        if not self.summaries_path.exists():
            return []
        with open(self.summaries_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.error("Could not decode summaries JSON file. Starting fresh.")
                return []

    def _save_summaries(self, summaries: List[Dict[str, Any]]):
        """Saves the updated list of summaries to the JSON file."""
        with open(self.summaries_path, 'w') as f:
            json.dump(summaries, f, indent=4)

    def process_document(self, message: Dict[str, Any]):
        """
        Callback function to process a single document notification from Kafka.
        """
        metadata = message.get('metadata', {})
        full_text = message.get('full_text')
        title = metadata.get('title', 'No Title')
        url = metadata.get('url')

        if not all([full_text, url]):
            logging.warning("Received message without full text or URL. Skipping.")
            return

        logging.info(f"Processing document for summary: {title}")

        # 1. Find related older documents by searching with the new document's title
        title_embedding = self.embedder.generate_embeddings([title])[0]
        search_results = self.vector_index.query(title_embedding, top_k=3)
        
        # Filter out the document itself from the search results to get only older context
        old_docs_texts = [
            res['metadata']['text'] for res in search_results 
            if res['metadata'].get('url') != url
        ]
        
        # 2. Generate the summary using the LLM
        summary = self.llm_generator.generate_digest_summary(full_text, old_docs_texts)
        
        # 3. Save the new summary to the persistent JSON file
        new_summary_entry = {
            "title": title,
            "url": url,
            "published_date": metadata.get('published', 'N/A'),
            "summary": summary,
            "timestamp": time.time()
        }
        
        summaries = self._load_summaries()
        summaries.append(new_summary_entry)
        self._save_summaries(summaries)
        
        logging.info(f"Successfully generated and saved summary for: {title}")

def main():
    """
    Main function to initialize and run the summarization service.
    """
    logging.info("Starting the Summarization Service...")
    config = Config()
    # Wait a bit longer to ensure the processor has time to start
    time.sleep(25)
    
    pipeline = SummarizationPipeline(config)
    
    # Initialize a Kafka consumer for the 'processed-documents' topic
    consumer = RegulatoryDataConsumer(
        bootstrap_servers=config.kafka_config.bootstrap_servers,
        group_id="summarizer-group",  # Use a unique group ID for this consumer
        topics=[config.kafka_config.processed_documents_topic]
    )
    
    logging.info("Initialization complete. Starting to consume processed documents...")
    consumer.consume_updates(pipeline.process_document)

if __name__ == "__main__":
    main()

