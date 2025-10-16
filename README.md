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
