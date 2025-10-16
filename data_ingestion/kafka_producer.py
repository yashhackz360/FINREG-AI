import json
import logging
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

class RegulatoryDataProducer:
    """
    Handles the connection and message sending to the Apache Kafka service.
    This class is responsible for producing messages about new regulatory documents.
    """
    def __init__(self, bootstrap_servers: str):
        self.logger = logging.getLogger(__name__)
        try:
            # Initialize the Kafka producer with connection details and serializers.
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=1000  # Wait 1s before retrying
            )
            self.logger.info("Kafka producer initialized successfully.")
        except KafkaError as e:
            self.logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None

    def send_update(self, topic: str, data: Dict[str, Any]):
        """Sends a single data payload to the specified Kafka topic."""
        if not self.producer:
            self.logger.error("Producer is not available. Cannot send message.")
            return

        try:
            # The source (e.g., 'rbi') is used as the key for partitioning.
            key = data.get('source')
            # Send the message and wait for acknowledgment.
            future = self.producer.send(topic, key=key, value=data)
            record_metadata = future.get(timeout=10)
            self.logger.info(f"Successfully sent update to topic '{record_metadata.topic}'")
        except KafkaError as e:
            self.logger.error(f"Failed to send update to Kafka topic '{topic}': {e}")

    def close(self):
        """Flushes any buffered messages and closes the producer connection."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            self.logger.info("Kafka producer closed.")

