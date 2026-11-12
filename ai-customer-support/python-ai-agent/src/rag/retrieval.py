from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter

from src.config import get_settings
from src.rag.models import RetrievalResult
from src.rag.llm_client import get_openai_compatible_client

class Retriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.qdrant = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
        )
        self.openai = get_openai_compatible_client()

    async def _embedding(self, query: str) -> list[float]:
        kwargs = {
            "model": self.settings.embedding_model,
            "input": query,
        }
        if self.settings.embedding_dimensions and "nemotron" not in self.settings.embedding_model:
            kwargs["dimensions"] = self.settings.embedding_dimensions
        result = await self.openai.embeddings.create(**kwargs)
        return result.data[0].embedding
    
    # def __init__(self) -> None:
    #     self.settings = get_settings()
    #     self.qdrant = QdrantClient(
    #         url=self.settings.qdrant_url,
    #         api_key=self.settings.qdrant_api_key,
    #     )
    #     self.openai = AsyncOpenAI(api_key=self.settings.openai_api_key)

    # async def _embedding(self, query: str) -> list[float]:
    #     result = await self.openai.embeddings.create(
    #         model=self.settings.embedding_model,
    #         input=query,
    #         dimensions=self.settings.embedding_dimensions,
    #     )
    #     return result.data[0].embedding

    async def semantic_search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        vector = await self._embedding(query)
        result = self.qdrant.query_points(
            collection_name=self.settings.qdrant_collection,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        points = getattr(result, "points", result)
        return [
            RetrievalResult(
                id=str(p.id),
                content=p.payload["content"],
                score=float(p.score),
                source=p.payload["source"],
                page=p.payload.get("page"),
                metadata=p.payload,
            )
            for p in points
        ]

    async def hybrid_search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        # The vector DB is the authoritative semantic index. A lightweight
        # lexical boost is applied to titles/content returned by the semantic
        # candidate set; this keeps the service dependency-light.
        candidates = await self.semantic_search(query, max(top_k * 3, 10))
        terms = {t.lower() for t in query.split() if len(t) > 2}

        scored = []
        for item in candidates:
            haystack = f"{item.content} {item.source}".lower()
            lexical = sum(1 for term in terms if term in haystack) / max(len(terms), 1)
            final_score = 0.75 * item.score + 0.25 * lexical
            scored.append((final_score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            item.model_copy(update={"score": score})
            for score, item in scored[:top_k]
        ]

    async def search(self, query: str, mode: str = "hybrid", top_k: int | None = None):
        k = top_k or self.settings.rag_top_k
        if mode == "semantic":
            return await self.semantic_search(query, k)
        return await self.hybrid_search(query, k)

    async def get_context(self, doc_id: str) -> RetrievalResult | None:
        points = self.qdrant.retrieve(
            collection_name=self.settings.qdrant_collection,
            ids=[doc_id],
            with_payload=True,
        )
        if not points:
            return None
        p = points[0]
        return RetrievalResult(
            id=str(p.id),
            content=p.payload["content"],
            score=1.0,
            source=p.payload["source"],
            page=p.payload.get("page"),
            metadata=p.payload,
        )
