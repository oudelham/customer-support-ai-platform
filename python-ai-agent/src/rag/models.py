from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    id: str
    content: str
    source: str
    page: int | None = None
    title: str | None = None
    category: str | None = None
    author: str | None = None
    updated_at: str | None = None
    embedding_version: str = "v1"


class RetrievalResult(BaseModel):
    id: str
    content: str
    score: float
    source: str
    page: int | None = None
    metadata: dict = Field(default_factory=dict)
