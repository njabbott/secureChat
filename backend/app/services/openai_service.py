"""OpenAI service for chat completions"""

import logging
from typing import List, Dict, Any
from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI chat completions"""

    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"Initialized OpenAI service with model: {self.model}")

    def generate_response(
        self, user_query: str, context_documents: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response using RAG (Retrieval Augmented Generation)

        Args:
            user_query: The user's question
            context_documents: Retrieved documents from vector DB

        Returns:
            Generated response text
        """
        try:
            # Build context from retrieved documents
            context_text = self._build_context(context_documents)

            # Create system prompt
            system_prompt = """You are Chat Magic, an intelligent assistant that helps users find information from their Confluence documentation.

Your role:
- Answer questions based on the provided Confluence documents
- Be concise and accurate
- If the answer is not in the provided context, say so clearly
- Always cite which Confluence page your information comes from
- Maintain a helpful and professional tone

Important: Only use information from the provided context. Do not make up information."""

            # Create user prompt with context
            user_prompt = f"""Context from Confluence:

{context_text}

User Question: {user_query}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, please say so."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            answer = response.choices[0].message.content
            logger.info(f"Generated response for query: {user_query[:50]}...")

            return answer

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise

    def _build_context(self, context_documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved documents

        Args:
            context_documents: List of documents from vector DB

        Returns:
            Formatted context string
        """
        if not context_documents:
            return "No relevant documents found."

        context_parts = []

        for i, doc in enumerate(context_documents, 1):
            metadata = doc.get("metadata", {})
            document_text = doc.get("document", "")

            title = metadata.get("title", "Unknown")
            space_name = metadata.get("space_name", "Unknown Space")
            url = metadata.get("url", "")

            context_part = f"""
Document {i}: {title} (from {space_name})
URL: {url}
Content: {document_text}
---
"""
            context_parts.append(context_part.strip())

        return "\n\n".join(context_parts)

    def summarize_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a summary of a conversation

        Args:
            messages: List of conversation messages

        Returns:
            Summary text
        """
        try:
            conversation_text = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in messages]
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following conversation in 2-3 sentences.",
                    },
                    {"role": "user", "content": conversation_text},
                ],
                temperature=0.5,
                max_tokens=150,
            )

            summary = response.choices[0].message.content
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Conversation summary unavailable"
