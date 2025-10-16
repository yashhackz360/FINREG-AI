import time
import logging
from src.config import Config
from data_ingestion.kafka_producer import RegulatoryDataProducer
from data_ingestion.regulatory_monitor import RegulatoryMonitor

# Configure logging to provide timestamps and severity levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [IngestionMonitor] - %(message)s'
)

def main():
    """
    Main function to initialize and run the regulatory data monitor.
    This service is responsible for polling RSS feeds and producing new document
    notifications to a Kafka topic.
    """
    logging.info("Starting the Regulatory Data Monitoring service...")
    config = Config()

    # A brief delay to ensure the Kafka broker is fully up and running in Docker Compose.
    logging.info("Waiting for Kafka to be ready...")
    time.sleep(15)

    producer = None  # Initialize producer to None
    try:
        # Initialize the Kafka producer to send messages
        producer = RegulatoryDataProducer(
            bootstrap_servers=config.kafka_config.bootstrap_servers
        )
        
        # Initialize the monitor that contains the main polling loop
        monitor = RegulatoryMonitor(
            kafka_producer=producer,
            rss_feeds=config.monitoring_config.rss_feeds,
            check_interval=config.monitoring_config.check_interval
        )
        
        logging.info("Initialization complete. Starting monitoring loop.")
        monitor.run()

    except Exception as e:
        logging.critical(f"A critical error occurred in the monitoring service: {e}", exc_info=True)
    finally:
        # Ensure the producer connection is closed gracefully on exit
        if producer:
            logging.info("Closing Kafka producer.")
            producer.close()

if __name__ == "__main__":
    main()

