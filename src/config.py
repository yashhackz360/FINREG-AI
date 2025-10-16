import os
from dataclasses import dataclass, field
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class KafkaConfig:
    """Dataclass for Kafka connection settings."""
    bootstrap_servers: str = "kafka:29092"
    # --- MODIFIED: Renamed original topic and added new topic ---
    ingestion_topic: str = "regulatory-updates"
    processed_documents_topic: str = "processed-documents"
    group_id: str = "rag-fintech-processor"

@dataclass
class MonitoringConfig:
    """Dataclass for data source monitoring settings."""
    rss_feeds: Dict[str, str] = field(default_factory=lambda: {
        "rbi": "https://rbi.org.in/Scripts/Rss.aspx",
        "sebi": "https://www.sebi.gov.in/sebirss.xml",
    })
    check_interval: int = 100

@dataclass
class PineconeConfig:
    """Dataclass for Pinecone vector database settings."""
    api_key: str
    index_name: str
    dimension: int
    metric: str

class Config:
    """Main configuration class for the entire application."""
    def __init__(self):
        # --- API Keys ---
        self.groq_api_key: str = os.getenv("GROQ_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")

        if not all([self.groq_api_key, pinecone_api_key]):
            raise ValueError("API keys for Groq and Pinecone must be set in the .env file.")

        # --- Model & RAG Settings ---
        self.embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
        self.llm_model: str = "llama-3.1-8b-instant"
        self.top_k_retrieval: int = 5
        
        # --- NEW: Path for generated summaries ---
        self.summaries_file_path: str = "artifacts/latest_summaries.json"

        # --- Component Configurations ---
        self.pinecone_config = PineconeConfig(
            api_key=pinecone_api_key,
            index_name=os.getenv("PINECONE_INDEX_NAME", "fintech-regulatory-rag"),
            dimension=384, 
            metric="cosine"
        )
        
        self.kafka_config = KafkaConfig()
        # This is corrected to use the right class name
        self.kafka_config.topics = [self.kafka_config.ingestion_topic]
        self.monitoring_config = MonitoringConfig()

