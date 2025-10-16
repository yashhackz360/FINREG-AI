import json
import logging
from typing import Callable, List
from kafka import KafkaConsumer
from kafka.errors import KafkaError

class RegulatoryDataConsumer:
    """
    A Kafka consumer that listens to a specified topic for regulatory updates.
    It processes incoming messages using a provided callback function.
    """
    def __init__(self, bootstrap_servers: str, group_id: str, topics: List[str]):
        """
        Initializes the Kafka Consumer.

        Args:
            bootstrap_servers (str): Comma-separated list of Kafka broker addresses.
            group_id (str): The consumer group ID.
            topics (List[str]): A list of topics to subscribe to.
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=bootstrap_servers.split(','),
                group_id=group_id,
                # Start reading from the earliest message if the consumer group is new
                auto_offset_reset='earliest',
                # Automatically commit offsets
                enable_auto_commit=True,
                # Decode the message value from JSON
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            self.logger.info(f"Kafka consumer initialized for group '{group_id}' on topics {topics}.")
        except KafkaError as e:
            self.logger.critical(f"Failed to initialize Kafka consumer: {e}", exc_info=True)
            # This is a critical failure, so we raise it to stop the service.
            raise

    def consume_updates(self, callback: Callable):
        """
        Starts an infinite loop to consume messages and process them with a callback.

        Args:
            callback (Callable): A function that will be called with the message
                                 value for each new message.
        """
        self.logger.info("Starting to consume updates from Kafka...")
        try:
            for message in self.consumer:
                self.logger.debug(f"Received message: {message.value}")
                try:
                    # Execute the processing logic provided by the caller
                    callback(message.value)
                except Exception as e:
                    self.logger.error(f"Error processing message: {message.value}. Error: {e}", exc_info=True)
                    # Continue to the next message
                    continue
        except KeyboardInterrupt:
            self.logger.info("Consumer stopped by user.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in the consumer loop: {e}", exc_info=True)
        finally:
            self.logger.info("Closing Kafka consumer.")
            if self.consumer:
                self.consumer.close()

