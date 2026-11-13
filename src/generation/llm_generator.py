import logging
import re
from groq import Groq
from typing import List, Dict, Any, Optional


class LLMGenerator:
    """
    Handles the generation of answers using the Groq API.
    This class constructs a precise prompt and interfaces with the LLM
    to synthesize answers based on retrieved context.
    """

    def __init__(self, api_key: str, model: str):
        self.logger = logging.getLogger(__name__)
        if not api_key:
            raise ValueError("Groq API key is required for LLMGenerator.")

        self.client = Groq(api_key=api_key)
        self.model = model
        self.logger.info(f"LLMGenerator initialized with model: {self.model}")

    def _build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Constructs a detailed prompt for the LLM, combining the user query,
        retrieved context, and optionally chat history.
        """
        # Extract context
        context_str = "\n\n---\n\n".join(
            [f"[Document: {chunk['metadata'].get('title', 'N/A')} | Published: {chunk['metadata'].get('published', 'unknown')} | Source: {chunk['metadata'].get('source', 'N/A')}]\n{chunk['metadata']['text']}"
             for chunk in context_chunks
             if 'metadata' in chunk and 'text' in chunk['metadata']]
        )
        if not context_str:
            context_str = "No relevant documents were found in the knowledge base."

        # Format chat history
        history_str = ""
        if chat_history:
            for message in chat_history[-4:]:  # Only last 4 messages
                history_str += f"{message['role'].capitalize()}: {message['content']}\n"

        # Final prompt
        prompt = f"""
        You are an expert financial-analyst AI specializing in Indian fintech regulations.

         Base every answer on the retrieved documents and the user’s current question.
         Draw on the full spectrum of Indian financial-technology rules, including but not limited to:
         Reserve Bank of India (RBI) directives (digital lending, P2P, payment aggregators, prepaid instruments, NBFC norms, KYC/AML).
         Securities and Exchange Board of India (SEBI) regulations (crowdfunding, investment advisors, algorithmic trading, fintech in securities markets).
         Insurance Regulatory and Development Authority of India (IRDAI) guidelines (insurtech, digital policies).
         Ministry of Finance notifications, Prevention of Money Laundering Act (PMLA) obligations, data-privacy requirements under the Digital Personal Data Protection Act, IT Act provisions, and cross-border payment rules.
         Recent circulars, master directions, press releases, and consultation papers from all relevant regulators.
         If the context or retrieved material does not contain the necessary detail, state clearly: “The information is not in the documents.”
         When helpful, flag regulatory gaps, pending consultations, or effective dates.
         Use prior chat history only for conversational continuity, not as a source of regulatory facts.
         STRICT GROUNDING: state only facts that appear in the RETRIEVED CONTEXT. Never invent dates, figures, circular numbers, thresholds or expansions of acronyms. Quote document titles and publication dates as given in the context headers, and mention the publication date when describing something as recent. For greetings or small talk, reply briefly without citing regulations.

        CHAT HISTORY:
        ---
        {history_str}
        ---

        RETRIEVED CONTEXT:
        ---
        {context_str}
        ---

        CURRENT QUESTION: {query}

        ANSWER:
        """.strip()
        return prompt

    PREFERRED_MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
    ]

    def _candidate_models(self) -> List[str]:
        """Configured model first, then preferred models that this key can actually access."""
        try:
            available = {m.id for m in self.client.models.list().data}
        except Exception as e:
            self.logger.warning(f"Could not list Groq models: {e}")
            return list(dict.fromkeys([self.model] + self.PREFERRED_MODELS))
        ordered = [m for m in [self.model] + self.PREFERRED_MODELS if m in available]
        if not ordered:  # fall back to any chat-capable model
            ordered = [m for m in sorted(available) if not re.search(r"whisper|orpheus|guard|safeguard|tts", m)]
        return list(dict.fromkeys(ordered))

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Sends the prompt to the Groq API and returns the generated answer.
        """
        prompt = self._build_prompt(query, context_chunks, chat_history)

        last_err = None
        for model in self._candidate_models():
            try:
                self.logger.info(f"Sending request to Groq API ({model}).")
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model,
                    temperature=0.1,
                    max_tokens=2048,
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                last_err = e
                self.logger.error(f"LLM call failed with {model}: {e}", exc_info=True)
        return f"Error: language model request failed ({type(last_err).__name__}: {str(last_err)[:200]})"

    # --- NEW METHODS FOR SUMMARIZATION ---
    def _build_summary_prompt(self, new_doc_text: str, old_docs_texts: Optional[List[str]] = None) -> str:
        """Builds a prompt for summarization, adapting if older context is available."""
        if old_docs_texts:
            # Comparison Prompt
            context_str = "\n\n---\n\n".join(old_docs_texts)
            prompt = f"""
            You are a compliance analyst. Your task is to identify and summarize the key changes or new introductions in a new regulatory document compared to older, related ones.

            OLDER RELATED DOCUMENTS:
            ---
            {context_str}
            ---

            NEW DOCUMENT:
            ---
            {new_doc_text}
            ---

            Based on the provided documents, summarize the most significant changes or new points introduced in the NEW DOCUMENT in three concise bullet points. If there are no significant changes, state that.
            """
        else:
            # Standalone Summary Prompt
            prompt = f"""
            You are a compliance analyst. Your task is to summarize a new regulatory document.

            NEW DOCUMENT:
            ---
            {new_doc_text}
            ---

            Summarize the key takeaways from this document in three concise bullet points.
            """
        return prompt.strip()

    def generate_digest_summary(self, new_doc_text: str, old_docs_texts: Optional[List[str]] = None) -> str:
        """Generates a summary, either comparative or standalone."""
        prompt = self._build_summary_prompt(new_doc_text, old_docs_texts)
        try:
            self.logger.info("Sending request to Groq API to generate summary.")
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
                max_tokens=1500,
            )
            summary = chat_completion.choices[0].message.content.strip()
            self.logger.info("Successfully received summary from Groq API.")
            return summary
        except Exception as e:
            self.logger.error(f"Failed to generate summary from LLM. Error: {e}", exc_info=True)
            return "Error: Could not generate summary."

