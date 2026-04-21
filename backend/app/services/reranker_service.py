"""Cross-encoder reranking service"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class RerankerService:
    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self):
        self._model: Optional[CrossEncoder] = None

    def _load_model(self) -> CrossEncoder:
        if self._model is None:
            logger.info(f"Loading cross-encoder model: {self.MODEL_NAME}")
            self._model = CrossEncoder(self.MODEL_NAME)
            logger.info("Cross-encoder model loaded")
        return self._model

    def _score(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        model = self._load_model()
        pairs = [(query, doc["document"]) for doc in documents]
        scores = model.predict(pairs)
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)
        return sorted(documents, key=lambda d: d["rerank_score"], reverse=True)

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []
        loop = asyncio.get_event_loop()
        ranked = await loop.run_in_executor(None, self._score, query, documents)
        return ranked[:top_n]
