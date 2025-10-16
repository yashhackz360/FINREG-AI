import logging
from typing import Dict, Any, List
from src.retrieval.embedder import Embedder
from src.retrieval.vector_index import VectorIndex
from src.generation.llm_generator import LLMGenerator
from src.retrieval.keyword_index import KeywordIndex

class RAGPipeline:
    """
    Orchestrates the entire Hybrid RAG pipeline (Keyword + Semantic).
    """
    def __init__(self, embedder: Embedder, vector_index: VectorIndex, llm_generator: LLMGenerator, top_k: int = 5):
        self.embedder = embedder
        self.vector_index = vector_index
        self.llm_generator = llm_generator
        self.keyword_index = KeywordIndex() 
        self.top_k = top_k
        self.logger = logging.getLogger(__name__)
        self.logger.info("RAG Pipeline with Hybrid Search initialized.")

    def _reciprocal_rank_fusion(self, search_results: List[List[Dict]], k: int = 60) -> List[Dict]:
        """Performs RRF on a list of search results."""
        fused_scores = {}
        
        for result_list in search_results:
            for rank, doc in enumerate(result_list):
                doc_id = doc['id']
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = 0
                fused_scores[doc_id] += 1 / (k + rank + 1)
        
        reranked_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        doc_map = {doc['id']: doc for res_list in search_results for doc in res_list}
        final_docs = [doc_map[doc_id] for doc_id, score in reranked_results if doc_id in doc_map]
        return final_docs

    def execute(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Executes the full RAG workflow for a given query and chat history.
        """
        self.logger.info(f"Executing Hybrid RAG pipeline for query: '{query}'")

        # 1. Perform Keyword Search
        bm25_results = self.keyword_index.search(query, top_k=self.top_k)
        self.logger.info(f"BM25 found {len(bm25_results)} results.")

        # 2. Perform Semantic Search
        query_embedding = self.embedder.generate_embeddings([query])
        if not query_embedding:
            return {"answer": "Error: Could not process the query.", "sources": []}
        
        vector_results_raw = self.vector_index.query(vector=query_embedding[0], top_k=self.top_k)
        vector_results = [{'id': res['id'], 'text': res['metadata']['text'], 'metadata': res['metadata']} for res in vector_results_raw]
        self.logger.info(f"Vector search found {len(vector_results)} results.")

        # 3. Fuse the results using RRF
        fused_results = self._reciprocal_rank_fusion([bm25_results, vector_results])
        retrieved_chunks = fused_results[:self.top_k]
        self.logger.info(f"Fused and reranked to {len(retrieved_chunks)} results.")

        # 4. Generate answer using the LLM, now with chat history
        answer = self.llm_generator.generate_answer(query, retrieved_chunks, chat_history)
        
        # 5. Process sources for citation
        sources, seen_urls = [], set()
        for chunk in retrieved_chunks:
            metadata = chunk.get('metadata', {})
            url = metadata.get('url')
            if url and url not in seen_urls:
                sources.append({
                    'title': metadata.get('title', 'N/A'),
                    'url': url,
                    'source': metadata.get('source', 'N/A')
                })
                seen_urls.add(url)
        
        self.logger.info("RAG pipeline execution complete.")
        return {"answer": answer, "sources": sources}

