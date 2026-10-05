from __future__ import annotations

from typing import Any, Annotated
import operator
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    user_input: str
    channel: str
    customer_id: str
    intent: str
    conversation_history: list[dict[str, Any]]
    context_data: dict[str, Any]
    selected_tools: list[str]
    final_response: str
    actions_taken: Annotated[list[str], operator.add]
    confidence: float
    requires_human: bool
    citations: list[dict[str, Any]]
    ticket_created: bool
    ticket_data: dict[str, Any] | None
    error: str | None
