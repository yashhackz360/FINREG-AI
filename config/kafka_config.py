from dataclasses import dataclass, field
from typing import List

@dataclass
class KafkaConfig:
    """
    Holds all configuration parameters for the Apache Kafka connection.
    Using a dataclass provides type hints and a clean structure.
    """
    # The address of the Kafka broker, as seen from other Docker containers.
    # The default value 'kafka:29092' matches the docker-compose.yml setup.
    bootstrap_servers: str = "kafka:29092"

    # A list of topics that the consumer will subscribe to.
    topics: List[str] = field(default_factory=lambda: ["regulatory-updates"])

    # The ID for the consumer group. All consumers with the same group ID
    # will work together to process messages from the topics.
    group_id: str = "rag-fintech-processor"
