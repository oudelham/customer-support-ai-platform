from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Iterable

from openai import AsyncOpenAI
from qdrant_client import QdrantClient, models
from pypdf import PdfReader
from docx import Document as DocxDocument

from src.config import get_settings
from src.rag.models import DocumentChunk
from src.rag.llm_client import get_openai_compatible_client


def extract_text(path: Path) -> list[tuple[str, int | None]]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return [(path.read_text(encoding="utf-8"), None)]

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return [(page.extract_text() or "", i + 1) for i, page in enumerate(reader.pages)]

    if suffix == ".docx":
        doc = DocxDocument(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(text, None)]

    return []


def chunk_text(text: str, max_chars: int, overlap: int) -> list[str]:
    # The project specification calls for ~1000-token chunks. Character-based
    # chunking is deliberately conservative and keeps paragraph boundaries.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if len(candidate) <= max_chars * 4:
            current = candidate
            continue

        if current:
            chunks.append(current)

        tail = current[-overlap * 4:] if overlap else ""
        current = f"{tail}\n\n{paragraph}".strip()

    if current:
        chunks.append(current)

    return chunks


async def embed(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    client = get_openai_compatible_client()  # from helper above
    kwargs = {
        "model": settings.embedding_model,
        "input": texts,
    }
    # Only pass dimensions if the model supports it
    if settings.embedding_dimensions and "nemotron" not in settings.embedding_model:
        kwargs["dimensions"] = settings.embedding_dimensions
    response = await client.embeddings.create(**kwargs)
    return [item.embedding for item in response.data]


# async def embed(texts: list[str]) -> list[list[float]]:
#     settings = get_settings()
#     client = AsyncOpenAI(api_key=settings.openai_api_key)
#     response = await client.embeddings.create(
#         model=settings.embedding_model,
#         input=texts,
#         dimensions=settings.embedding_dimensions,
#     )
#     return [item.embedding for item in response.data]


def deterministic_id(source: str, content: str, index: int) -> str:
    raw = f"{source}|{index}|{content}".encode()
    return hashlib.md5(raw).hexdigest()


async def index_directory(directory: str) -> int:
    settings = get_settings()
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    existing = [c.name for c in qdrant.get_collections().collections]
    if settings.qdrant_collection not in existing:
        qdrant.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.embedding_dimensions,
                distance=models.Distance.COSINE,
            ),
        )

    chunks: list[DocumentChunk] = []
    for path in Path(directory).rglob("*"):
        if not path.is_file():
            continue
        for page_text, page in extract_text(path):
            pieces = chunk_text(
                page_text,
                settings.rag_chunk_size,
                settings.rag_chunk_overlap,
            )
            for i, piece in enumerate(pieces):
                chunks.append(
                    DocumentChunk(
                        id=deterministic_id(str(path), piece, i),
                        content=piece,
                        source=str(path),
                        page=page,
                        title=path.stem,
                    )
                )

    if not chunks:
        return 0

    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        vectors = await embed([c.content for c in batch])
        points = [
            models.PointStruct(
                id=c.id,
                vector=vector,
                payload=c.model_dump(),
            )
            for c, vector in zip(batch, vectors)
        ]
        qdrant.upsert(settings.qdrant_collection, points=points)

    return len(chunks)


if __name__ == "__main__":
    import asyncio
    directory = sys.argv[1] if len(sys.argv) > 1 else "knowledge"
    count = asyncio.run(index_directory(directory))
    print(f"Indexed {count} chunks")
