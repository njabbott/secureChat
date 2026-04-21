"""Chat endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..config import settings
from ..models.chat import ChatMessage, ChatResponse, JiraTicket
from ..services import (
    VectorDBService,
    OpenAIService,
    PIIService,
    RerankerService,
    JiraService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Service instances (will be initialized in main.py and injected)
vector_db_service: VectorDBService = None
openai_service: OpenAIService = None
pii_service: PIIService = None
reranker_service: RerankerService = None
jira_service: JiraService = None


def get_services():
    """Dependency to ensure services are initialized"""
    if not all([vector_db_service, openai_service, pii_service, reranker_service, jira_service]):
        raise HTTPException(status_code=500, detail="Services not initialized")
    return vector_db_service, openai_service, pii_service, reranker_service, jira_service


def _reciprocal_rank_fusion(ranked_lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
    scores: Dict[str, float] = {}
    payloads: Dict[str, Dict] = {}
    for lst in ranked_lists:
        for rank, doc in enumerate(lst, start=1):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in payloads:
                payloads[doc_id] = doc
    return [
        {**payloads[doc_id], "rrf_score": score}
        for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ]


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
        vector_db, openai, pii, reranker, jira = get_services()

        logger.info(f"Received message: {message.message[:50]}...")

        # Step 1: Check for PII and anonymize if needed
        anonymized_query, pii_info = pii.detect_and_anonymize(message.message)

        pii_filtered = pii_info.total_count > 0
        if pii_filtered:
            logger.info(
                f"PII detected and filtered: {pii_info.total_count} items - {pii_info.entities}"
            )

        # Step 2: Hybrid retrieval + reranking
        query_text = anonymized_query if pii_filtered else message.message
        top_k = settings.hybrid_search_top_k
        vector_results = vector_db.query(query_text, n_results=top_k)
        bm25_results = vector_db.bm25_query(query_text, n_results=top_k)
        merged = _reciprocal_rank_fusion([vector_results, bm25_results])[:top_k]
        relevant_docs = await reranker.rerank(query_text, merged, top_n=settings.rerank_top_n)

        # Step 3: Generate response via OpenAI with RAG + Jira function calling
        response_text, tool_call = openai.generate_response_with_tools(query_text, relevant_docs)

        # Step 3.5: Handle Jira ticket creation if model requested it
        jira_ticket = None
        if tool_call and tool_call["name"] == "create_jira_ticket":
            ticket_data = jira.create_ticket(**tool_call["args"])
            jira_ticket = JiraTicket(**ticket_data)
            response_text = (
                f"I've created Jira ticket **{jira_ticket.key}** for you.\n\n"
                f"**{jira_ticket.summary}** ({jira_ticket.issue_type})\n"
                f"View it here: {jira_ticket.url}"
            )

        # Step 3.6: Filter PII from response before returning to user
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
        # Offer ticket creation when no relevant docs found and we didn't already create one.
        # Reranker scores below 0 indicate the top result is not meaningfully relevant.
        top_score = max((d.get("rerank_score", -999) for d in relevant_docs), default=-999)
        suggest_ticket = jira_ticket is None and top_score < 0

        response = ChatResponse(
            response=filtered_response_text,
            sources=sources,
            pii_filtered=pii_filtered,
            pii_info=pii_info if pii_filtered else None,
            session_id=message.session_id,
            jira_ticket=jira_ticket,
            suggest_ticket=suggest_ticket,
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
        vector_db, _, _, _ = get_services()
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
