
# FinReg AI: Real-Time Indian Fintech Regulatory Assistant

[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)  
[![Python](https://img.shields.io/badge/Python-3.9+-green?logo=python)](https://www.python.org/)  
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-streaming-black?logo=apachekafka)](https://kafka.apache.org/)  
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-orange)](https://www.pinecone.io/)  
[![Groq](https://img.shields.io/badge/Groq-LLM%20Inference-red)](https://groq.com/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-UI%20Framework-FF4B4B?logo=streamlit)](https://streamlit.io/)  

FinReg AI is a production-grade Retrieval-Augmented Generation (RAG) system designed to deliver **accurate, real-time answers on Indian financial regulations**.  
It continuously ingests official publications from the **Reserve Bank of India (RBI)** and the **Securities and Exchange Board of India (SEBI)**, builds an evolving knowledge base, and provides **source-backed answers** via a conversational interface.

---

## ✨ Key Features

- **Real-Time Data Ingestion**: Monitors RBI and SEBI RSS feeds for new publications.  
- **Event-Driven Architecture**: Built on Apache Kafka with a multi-stage pipeline to decouple discovery, indexing, and summarization.  
- **Automated Regulatory Summaries**: A dedicated microservice generates concise, AI-powered summaries of the latest documents.  
- **Hybrid Search**: BM25 keyword search + semantic vector search with Reciprocal Rank Fusion (RRF).  
- **Vector Database**: Pinecone stores embeddings for scalable semantic retrieval.  
- **Low-Latency LLM**: Groq API provides high-speed inference for responses.  
- **Conversational UI**: Streamlit app supports chat history and displays linked sources.  
- **Containerized Deployment**: Docker Compose orchestrates all services.

---

## 🏛️ Architecture

```

Regulatory Feeds (RBI, SEBI)
│
└─> (1) Regulatory Monitor (Producer)
│
└─> Kafka Topic: "regulatory-updates"
│
└─> (2) Real-Time Processor (Consumer/Producer)
│
┌───────────┴──────────┐
│                      │
▼                      ▼
Pinecone (Vectors) &     Kafka Topic: "processed-documents"
BM25 Index (Keywords)          │
└─> (3) Summarizer Service (Consumer)
│
▼
artifacts/latest_summaries.json
│
│ (Reads Summaries)
│ (Sends Queries)
│
┌───────────────────────────────────────────────────────────────┘
│
└─> (4) Streamlit UI <=> RAG Pipeline <=> Groq LLM API

````

**Data Flow**  
1. **Discover**: `Regulatory Monitor` polls RSS feeds.  
2. **Event 1**: Publishes new docs to `regulatory-updates`.  
3. **Consume & Process**: `Real-Time Processor` fetches, cleans, and chunks documents.  
4. **Index**: Upserts chunks into Pinecone + BM25.  
5. **Event 2**: Publishes cleaned docs to `processed-documents`.  
6. **Summarize**: `Summarizer Service` creates summaries, saves JSON.  
7. **Query**: RAG pipeline fuses vector + keyword results.  
8. **Answer**: Groq LLM generates context-backed responses.

---

## 🚀 Getting Started

### Prerequisites
- Docker + Docker Compose  
- Python 3.9+  
- API keys: Pinecone, Groq  

### Setup

1. **Clone Repo**
   ```bash
   git clone https://github.com/your-username/RAG-FINTECH-REGULATOR.git
   cd RAG-FINTECH-REGULATOR
````

2. **Environment Variables**

   ```bash
   cp .env.example .env
   ```

   Add your API keys:

   ```env
   PINECONE_API_KEY="YOUR_PINECONE_API_KEY"
   PINECONE_INDEX_NAME="fintech-regulatory-rag"
   GROQ_API_KEY="YOUR_GROQ_API_KEY"
   ```

3. **Streamlit Secrets**

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Add same keys in `secrets.toml`.

4. **Clean Setup**

   ```bash
   docker compose down --volumes
   rm -f artifacts/*.pkl artifacts/*.json
   ```

5. **Build & Launch**

   ```bash
   docker compose up --build
   ```

6. **Access**

   * Chat UI: [http://localhost:8501](http://localhost:8501)
   * Kafka Monitor (AKHQ): [http://localhost:8080](http://localhost:8080)

---

## 🔧 Usage

Ask regulatory queries via the Streamlit chat UI. Summaries update automatically in the sidebar.

**Example Queries**

* *Semantic*: “Summarize RBI’s master direction on digital lending.”
* *Keyword*: “Find details on Priority Sector Lending (PSL).”
* *Conversational*: “What are the main categories within PSL?”

---

## 📂 Project Structure

```
RAG-FINTECH-REGULATOR/
├── .streamlit/
│   └── secrets.toml              # Streamlit secrets
├── app/
│   └── streamlit_ui.py           # Streamlit frontend
├── artifacts/                    # State, indexes, summaries
├── data_ingestion/
│   ├── kafka_producer.py         # Kafka producer utility
│   └── regulatory_monitor.py     # RSS monitoring loop
├── scripts/
│   ├── 01_ingest_data.py         # Producer entrypoint
│   ├── 02_realtime_ingestion.py  # Consumer/indexer entrypoint
│   └── 03_summarizer.py          # Summarizer entrypoint
├── src/
│   ├── config.py
│   ├── generation/llm_generator.py
│   ├── pipeline/rag_pipeline.py
│   ├── processing/document_processor.py
│   └── retrieval/
│       ├── embedder.py
│       ├── keyword_index.py
│       └── vector_index.py
├── streaming/
│   ├── kafka_consumer.py
│   ├── document_processor.py
│   └── vector_updater.py
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 📬 Connect

[LinkedIn – Yashwanth Kasarabada](https://www.linkedin.com/in/yashwanth-kasarabada-ba4265258/)

```
