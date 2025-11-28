"""Chat endpoints"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models.chat import ChatMessage, ChatResponse
from ..services import (
    VectorDBService,
    OpenAIService,
    PIIService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Service instances (will be initialized in main.py and injected)
vector_db_service: VectorDBService = None
openai_service: OpenAIService = None
pii_service: PIIService = None


def get_services():
    """Dependency to ensure services are initialized"""
    if not all([vector_db_service, openai_service, pii_service]):
        raise HTTPException(status_code=500, detail="Services not initialized")
    return vector_db_service, openai_service, pii_service


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """
    Send a message to the chatbot and get a response

    Args:
        message: User message

    Returns:
        ChatResponse with answer and sources
    """
    try:
        vector_db, openai, pii = get_services()

        logger.info(f"Received message: {message.message[:50]}...")

        # Step 1: Check for PII and anonymize if needed
        anonymized_query, pii_info = pii.detect_and_anonymize(message.message)

        pii_filtered = pii_info.total_count > 0
        if pii_filtered:
            logger.info(
                f"PII detected and filtered: {pii_info.total_count} items - {pii_info.entities}"
            )

        # Step 2: Query vector database for relevant documents
        query_text = anonymized_query if pii_filtered else message.message
        relevant_docs = vector_db.query(query_text, n_results=5)

        # Step 3: Generate response using OpenAI with RAG
        response_text = openai.generate_response(query_text, relevant_docs)

        # Step 3.5: Filter PII from OpenAI response before returning to user
        filtered_response_text, response_pii_info = pii.detect_and_anonymize(
            response_text,
            replacement_text="[PII redacted]"
        )

        if response_pii_info.total_count > 0:
            logger.warning(
                f"PII detected in OpenAI response and filtered: {response_pii_info.total_count} items - {response_pii_info.entities}"
            )

        # Step 4: Prepare sources
        sources = []
        seen_urls = set()  # Avoid duplicate sources

        for doc in relevant_docs:
            metadata = doc.get("metadata", {})
            url = metadata.get("url", "")

            # Skip duplicates (multiple chunks from same document)
            if url in seen_urls:
                continue

            seen_urls.add(url)

            sources.append(
                {
                    "title": metadata.get("title", "Unknown"),
                    "space": metadata.get("space_name", "Unknown"),
                    "url": url,
                }
            )

        # Step 5: Build response
        response = ChatResponse(
            response=filtered_response_text,  # Use filtered response
            sources=sources,
            pii_filtered=pii_filtered,
            pii_info=pii_info if pii_filtered else None,
            session_id=message.session_id,
        )

        logger.info("Successfully generated chat response")
        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        vector_db, openai, pii = get_services()
        doc_count = vector_db.get_document_count()

        return {
            "status": "healthy",
            "vector_db_initialized": True,
            "openai_initialized": True,
            "pii_service_initialized": True,
            "indexed_documents": doc_count,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }
