from typing import Any
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    content: str


class InvokeRequest(BaseModel):
    message: str = Field(min_length=1)
    customerId: str | None = None
    customerEmail: str | None = None
    customerTier: str | None = None
    sessionId: str
    conversationHistory: list[ConversationMessage] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    response: str
    suggestedActions: list[str] = Field(default_factory=list)
    ticketCreated: bool = False
    ticketData: dict[str, Any] | None = None
    confidence: float = 0.0
    sources: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str
    channel: str = "api"
    customer_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    confidence: float
    requires_human: bool
    actions_taken: list[str] = Field(default_factory=list)
    citations: list[dict[str, Any]] = Field(default_factory=list)
