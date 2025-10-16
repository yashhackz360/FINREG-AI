import time
import logging
from src.config import Config
from src.retrieval.embedder import Embedder
from src.retrieval.vector_index import VectorIndex
from streaming.kafka_consumer import RegulatoryDataConsumer
from streaming.document_processor import RealTimeDocumentProcessor
from streaming.vector_updater import RealTimeVectorUpdater
from src.retrieval.keyword_index import KeywordIndex
from data_ingestion.kafka_producer import RegulatoryDataProducer

# Configure logging for this specific service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [RealtimeProcessor] - %(message)s'
)

class IngestionPipeline:
    """
    A class that encapsulates the logic for the real-time ingestion pipeline.
    It processes messages from Kafka, updates the knowledge base, and then
    triggers the downstream summarization service.
    """
    def __init__(self, config: Config):
        logging.info("Initializing Real-Time Ingestion Pipeline...")
        self.config = config
        self.processor = RealTimeDocumentProcessor()
        
        embedder = Embedder(config.embedding_model)
        vector_index = VectorIndex(config.pinecone_config)
        
        self.updater = RealTimeVectorUpdater(vector_index, embedder)
        self.keyword_updater = KeywordIndex()
        
        # Initialize a Kafka producer to send messages to the summarizer
        self.producer = RegulatoryDataProducer(config.kafka_config.bootstrap_servers)
        logging.info("Ingestion Pipeline initialized successfully.")

    def process_message(self, update_data: dict):
        """
        Callback function to handle a single message from the Kafka consumer.
        """
        url = update_data.get('url', 'N/A')
        logging.info(f"Received message to process document: {url}")
        
        # Process the document to get both chunks and the full cleaned text
        chunks, full_text = self.processor.process_update(update_data)
        
        if chunks:
            # Update the primary search indexes (Vector DB and Keyword Index)
            logging.info(f"Document chunked successfully. Updating databases with {len(chunks)} chunks.")
            self.updater.update_vectors(chunks)
            self.keyword_updater.update_index(chunks)
            
            # --- TRIGGER SUMMARIZER ---
            # After successful processing, send a message to the new topic
            logging.info("Producing message to trigger summarization service.")
            message_for_summarizer = {
                'metadata': update_data,
                'full_text': full_text
            }
            self.producer.send_update(
                self.config.kafka_config.processed_documents_topic,
                message_for_summarizer
            )
        else:
            logging.warning(f"No chunks were created for document: {url}. Skipping updates.")

def main():
    """
    Main function to initialize and run the real-time ingestion consumer.
    """
    logging.info("Starting the Real-Time Ingestion Service...")
    config = Config()

    logging.info("Waiting for services to be ready...")
    time.sleep(20)
    
    pipeline = IngestionPipeline(config)
    
    consumer = RegulatoryDataConsumer(
        bootstrap_servers=config.kafka_config.bootstrap_servers,
        group_id=config.kafka_config.group_id,
        topics=[config.kafka_config.ingestion_topic]
    )
    
    logging.info("Initialization complete. Starting to consume updates...")
    consumer.consume_updates(pipeline.process_message)

if __name__ == "__main__":
    main()

