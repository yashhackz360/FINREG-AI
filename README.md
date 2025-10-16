````markdown
# ⚖️ FinReg AI: Real-Time Indian Fintech Regulatory Assistant 🇮🇳  

![ui_image_ss](ui.png)

## 🌟 Overview  

FinReg AI is your **real-time assistant for Indian financial regulations**. 🏦  
It continuously ingests and processes updates from **RBI (Reserve Bank of India)** and **SEBI (Securities and Exchange Board of India)** to deliver:  

-   🔍 Accurate, up-to-date regulatory answers  
-   📚 Source-backed responses with linked references  
-   🤖 AI-powered summaries and insights  
-   💬 Conversational Q&A through a sleek Streamlit UI  

This platform is built to support **financial institutions, compliance teams, and fintech developers** with fast, reliable access to complex regulatory frameworks.  

---

## ✨ Key Features  

-   **⚡ Real-Time Data Ingestion:** Polls RBI & SEBI RSS feeds automatically.  
-   **🔄 Event-Driven Pipeline:** Apache Kafka decouples discovery, processing, and summarization.  
-   **🧾 Automated Summaries:** AI service produces concise, actionable briefs of regulatory documents.  
-   **🔍 Hybrid Search:** Combines BM25 keyword retrieval with semantic vector search via Pinecone.  
-   **🤖 High-Speed LLM Inference:** Powered by **Groq API** for lightning-fast responses.  
-   **💬 Conversational Interface:** Streamlit-based UI with chat history and source links.  
-   **🐳 Containerized Deployment:** End-to-end orchestration with Docker Compose.  

---

## 🛠️ Tech Stack  

-   🐍 **Python 3.9+** – Core programming language  
-   🐳 **Docker & Docker Compose** – Deployment & orchestration  
-   💬 **Streamlit** – Conversational UI  
-   📡 **Apache Kafka** – Event-driven streaming backbone  
-   📚 **BM25 & Pinecone Vector DB** – Hybrid retrieval  
-   🚀 **Groq API** – LLM inference for Q&A  
-   🧠 **RAG Pipeline** – Context-aware answers with source grounding  

---

## 🚀 Get Started  

### 1. Clone the Repository  
```bash
git clone https://github.com/your-username/RAG-FINTECH-REGULATOR.git
cd RAG-FINTECH-REGULATOR
````

### 2. Set Environment Variables

```bash
cp .env.example .env
```

Add your keys:

```env
PINECONE_API_KEY="YOUR_PINECONE_API_KEY"
PINECONE_INDEX_NAME="fintech-regulatory-rag"
GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

### 3. Configure Streamlit Secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Paste the same keys inside `secrets.toml`.

### 4. Clean Setup

```bash
docker compose down --volumes
rm -f artifacts/*.pkl artifacts/*.json
```

### 5. Build & Launch

```bash
docker compose up --build
```

### 6. Access Services

* 💬 Chat UI: [http://localhost:8501](http://localhost:8501)
* 📡 Kafka Monitor (AKHQ): [http://localhost:8080](http://localhost:8080)

---

## 🗂️ Project Structure

```
RAG-FINTECH-REGULATOR/
├── .streamlit/
│   └── secrets.toml              # 🔑 Streamlit secrets
├── app/
│   └── streamlit_ui.py           # 💬 Conversational UI
├── artifacts/                    # 📦 Summaries, indexes, state
├── data_ingestion/
│   ├── kafka_producer.py         # 📡 Kafka producer utility
│   └── regulatory_monitor.py     # 📰 Stage 1 – Discover
├── scripts/
│   ├── 01_ingest_data.py         # 🚀 Entrypoint – Stage 1
│   ├── 02_realtime_ingestion.py  # ⚡ Entrypoint – Stage 2
│   └── 03_summarizer.py          # 🧾 Entrypoint – Stage 3
├── src/
│   ├── config.py                 # ⚙️ Configurations
│   ├── generation/llm_generator.py   # 🤖 Stage 8 – Answer generation
│   ├── pipeline/rag_pipeline.py      # 🔄 Stage 7 – RAG query fusion
│   ├── processing/document_processor.py # 🧹 Stage 2 – Cleaning & chunking
│   └── retrieval/
│       ├── embedder.py           # 🧠 Embedding model
│       ├── keyword_index.py      # 🔍 BM25 keyword index
│       └── vector_index.py       # 📚 Pinecone vector index
├── streaming/
│   ├── kafka_consumer.py         # 📡 Stage 2 – Consumer
│   ├── document_processor.py     # 🧹 Real-time doc processor
│   └── vector_updater.py         # 📚 Vector DB updater
├── .env                          # 🔑 Environment variables
├── docker-compose.yml            # 🐳 Orchestration
├── Dockerfile                    # 🐳 Build container
└── requirements.txt              # 📦 Dependencies
```

---

## 🧩 Module Breakdown

* **📰 Data Ingestion (Stage 1):** Monitors RBI/SEBI feeds → publishes updates.
* **⚡ Processing & Indexing (Stage 2–4):** Cleans, chunks, and stores documents in BM25 + Pinecone.
* **🧾 Summarization (Stage 3):** Generates summaries, stores JSON.
* **🔄 RAG Pipeline (Stage 7):** Combines semantic + keyword search for robust retrieval.
* **🤖 Answer Generator (Stage 8):** Uses Groq API for context-backed responses.
* **💬 UI (Stage 4):** Streamlit frontend for queries and interactive use.

---

## 📜 Example Queries

* “Summarize RBI’s master direction on digital lending.”
* “Find details on Priority Sector Lending (PSL).”
* “What are the main categories within PSL?”

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, implement improvements, and open a pull request.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

📫 Connect with me on [LinkedIn](https://www.linkedin.com/in/yashwanth-kasarabada-ba4265258/)

```
