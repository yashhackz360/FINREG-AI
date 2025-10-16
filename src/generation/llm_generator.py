import logging
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
            [chunk['metadata']['text']
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

        try:
            self.logger.info("Sending request to Groq API to generate answer.")
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.1,  # Lower temperature for factual responses
                max_tokens=1024,
            )
            answer = chat_completion.choices[0].message.content.strip()
            self.logger.info("Successfully received answer from Groq API.")
            return answer
        except Exception as e:
            self.logger.error(
                f"Failed to generate answer from LLM. Error: {e}", exc_info=True
            )
            return "Error: There was an issue communicating with the language model."

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
                max_tokens=512,
            )
            summary = chat_completion.choices[0].message.content.strip()
            self.logger.info("Successfully received summary from Groq API.")
            return summary
        except Exception as e:
            self.logger.error(f"Failed to generate summary from LLM. Error: {e}", exc_info=True)
            return "Error: Could not generate summary."

