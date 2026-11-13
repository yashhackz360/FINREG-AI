"""
Batch refresh of the FinReg AI knowledge base (no Kafka needed).

Fetches RBI/SEBI RSS feeds, skips already-indexed documents, then for each new one:
  - chunks + embeds the text and upserts to Pinecone
  - updates the BM25 keyword index
  - generates an LLM summary and appends it to artifacts/latest_summaries.json

Usage:  python scripts/refresh_data.py [--max-new 15]
Requires env vars: GROQ_API_KEY, PINECONE_API_KEY, (PINECONE_INDEX_NAME)
"""
import argparse
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
import requests
from bs4 import BeautifulSoup

from src.config import Config
from src.generation.llm_generator import LLMGenerator
from src.retrieval.embedder import Embedder
from src.retrieval.keyword_index import KeywordIndex
from src.retrieval.vector_index import VectorIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("refresh")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
FEEDS = {
    "sebi": "https://www.sebi.gov.in/sebirss.xml",
    "rbi": "https://rbi.org.in/Scripts/Rss.aspx",
}


def fetch_entries():
    entries = []
    for source, url in FEEDS.items():
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            log.info(f"{source}: {len(feed.entries)} feed entries")
            for e in feed.entries:
                if e.get("link"):
                    entries.append({
                        "source": source,
                        "title": e.get("title", "No Title"),
                        "url": e["link"],
                        "published": e.get("published", ""),
                        "description": BeautifulSoup(e.get("summary", ""), "html.parser").get_text(" ", strip=True),
                    })
        except Exception as ex:
            log.warning(f"Could not fetch {source} feed: {ex}")
    return entries


def fetch_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception as ex:
        log.warning(f"Could not fetch {url}: {ex}")
        return ""


def chunk_text(text, size=1000, overlap=150):
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new", type=int, default=15)
    args = ap.parse_args()

    config = Config()
    kw = KeywordIndex()
    docs, _ = kw._load_from_disk()
    seen = {d["id"].split("_")[0] for d in docs}

    summaries_path = Path(config.summaries_file_path)
    summaries = json.loads(summaries_path.read_text(encoding="utf-8")) if summaries_path.exists() else []
    seen_urls = {s.get("url") for s in summaries}

    entries = fetch_entries()
    new = []
    for e in entries:
        doc_id = hashlib.md5(e["url"].encode()).hexdigest()
        if doc_id not in seen and e["url"] not in seen_urls:
            e["doc_id"] = doc_id
            new.append(e)
    log.info(f"{len(new)} new documents (processing up to {args.max_new})")
    new = new[: args.max_new]
    if not new:
        log.info("Nothing new. Done.")
        return

    embedder = Embedder(config.embedding_model)
    vindex = VectorIndex(config.pinecone_config)
    llm = LLMGenerator(api_key=config.groq_api_key, model=config.llm_model)

    for e in reversed(new):  # oldest first so newest ends up last in the summaries file
        text = fetch_text(e["url"])
        if len(text) < 200:
            text = f"{e['title']}. {e['description']}"
        text = text[:30000]
        meta_base = {k: e[k] for k in ("source", "title", "url", "published")}
        chunks = [
            {"id": f"{e['doc_id']}_{i}", "text": t, "metadata": {**meta_base, "text": t}}
            for i, t in enumerate(chunk_text(text))
        ]
        embeddings = embedder.generate_embeddings([c["text"] for c in chunks])
        if len(embeddings) != len(chunks):
            log.error(f"Embedding failed for {e['url']}, skipping")
            continue
        vindex.upsert_vectors([
            {"id": c["id"], "values": emb, "metadata": c["metadata"]} for c, emb in zip(chunks, embeddings)
        ])
        kw.update_index(chunks)

        summary = llm.generate_digest_summary(text[:8000], None)
        summaries.append({
            "title": e["title"],
            "url": e["url"],
            "published_date": e["published"],
            "summary": summary,
            "timestamp": time.time(),
        })
        log.info(f"Indexed + summarized: {e['title'][:80]}")

    summaries_path.parent.mkdir(parents=True, exist_ok=True)
    summaries_path.write_text(json.dumps(summaries[-100:], indent=4), encoding="utf-8")
    log.info(f"Refresh complete: {len(new)} documents processed.")


if __name__ == "__main__":
    main()
