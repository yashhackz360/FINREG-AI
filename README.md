
# FinReg AI: Real-Time Indian Fintech Regulatory Assistant

<div align="center">

<a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-ready-blue?logo=docker"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-green?logo=python"></a>
<a href="https://kafka.apache.org/"><img src="https://img.shields.io/badge/Apache%20Kafka-streaming-black?logo=apachekafka"></a>
<a href="https://www.pinecone.io/"><img src="https://img.shields.io/badge/Pinecone-Vector%20DB-orange"></a>
<a href="https://groq.com/"><img src="https://img.shields.io/badge/Groq-LLM%20Inference-red"></a>
<a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-UI%20Framework-FF4B4B?logo=streamlit"></a>

</div>

![ui_Screenshot(finreg_ai _final.png)


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

## 🚀 Setup

### Prerequisites
- Docker + Docker Compose  
- Python 3.9+  
- API keys: Pinecone, Groq  

### Installation

1. **Clone Repo**
   ```bash
   git clone https://github.com/your-username/RAG-FINTECH-REGULATOR.git
   cd RAG-FINTECH-REGULATOR


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

   Add the same keys in `secrets.toml`.

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

## 📂 Project Structure

```
RAG-FINTECH-REGULATOR/
├── .streamlit/
│   └── secrets.toml                  # Streamlit secrets
├── app/
│   └── streamlit_ui.py               # Stage 4 – UI
├── artifacts/                        # State, indexes, summaries
├── data_ingestion/
│   ├── kafka_producer.py             # Stage 1 – Producer
│   └── regulatory_monitor.py         # Stage 1 – Discover
├── scripts/
│   ├── 01_ingest_data.py             # Stage 1 – Entrypoint
│   ├── 02_realtime_ingestion.py      # Stage 2 – Process/Index
│   └── 03_summarizer.py              # Stage 3 – Summarize
├── src/
│   ├── config.py                     # Global configs
│   ├── generation/llm_generator.py   # Stage 8 – Answer
│   ├── pipeline/rag_pipeline.py      # Stage 7 – Query Fusion
│   ├── processing/document_processor.py # Stage 2 – Cleaning & chunking
│   └── retrieval/
│       ├── embedder.py               # Stage 4 – Embedding
│       ├── keyword_index.py          # Stage 4 – BM25 Index
│       └── vector_index.py           # Stage 4 – Pinecone Index
├── streaming/
│   ├── kafka_consumer.py             # Stage 2 – Consumer
│   ├── document_processor.py         # Stage 2 – Streaming processor
│   └── vector_updater.py             # Stage 4 – Index updater
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🔧 Usage

Ask regulatory queries via the Streamlit chat UI. Summaries update automatically in the sidebar.

**Example Queries**

* “Summarize RBI’s master direction on digital lending.”
* “Find details on Priority Sector Lending (PSL).”
* “What are the main categories within PSL?”

---

## 📬 Connect

[LinkedIn – Yashwanth Kasarabada](https://www.linkedin.com/in/yashwanth-kasarabada-ba4265258/)


