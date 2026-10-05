from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Header

from src.agent.main import agent_graph
from src.api.models import ChatRequest, ChatResponse, InvokeRequest, InvokeResponse
from src.api.session import SessionStore
from src.config import get_settings
from src.logging_config import configure_logging, audit

configure_logging(get_settings().log_level)
logger = logging.getLogger(__name__)
sessions = SessionStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI service starting")
    yield
    logger.info("AI service stopping")


app = FastAPI(title="Enterprise AI Integration Platform - AI Service", version="0.2.0", lifespan=lifespan)


def check_key(value: str | None):
    expected = get_settings().ai_agent_api_key
    if expected and value != expected:
        raise HTTPException(status_code=401, detail="Invalid AI service key")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "python-ai-agent"}


async def invoke_impl(request: InvokeRequest) -> InvokeResponse:
    previous = await sessions.get(request.sessionId)
    history = [m.model_dump() for m in request.conversationHistory]
    if not history:
        history = previous.get("conversation_history", [])
    history.append({"role": "user", "content": request.message})

    initial = {
        "user_input": request.message,
        "channel": "java",
        "customer_id": request.customerId or "",
        "conversation_history": history[-20:],
        "context_data": {
            **previous.get("context_data", {}),
            **request.context,
            "customer_email": request.customerEmail,
            "customer_tier": request.customerTier,
        },
        "actions_taken": [],
    }
    if get_settings().mock_llm:
        result = {
            "intent": "support", "confidence": 0.85, "requires_human": False,
            "final_response": f"Mock AI response for customer {request.customerId}: {request.message}",
            "actions_taken": ["mock_agent_completed"], "citations": [],
            "ticket_created": False, "ticket_data": None, "context_data": initial["context_data"],
        }
    else:
        result = await agent_graph.ainvoke(initial)
    response = result.get("final_response", "")

    history.append({"role": "assistant", "content": response})
    await sessions.save(request.sessionId, {
        "conversation_history": history[-20:],
        "context_data": result.get("context_data", {}),
        "last_intent": result.get("intent"),
    })

    return InvokeResponse(
        response=response,
        suggestedActions=["Human review"] if result.get("requires_human") else [],
        ticketCreated=bool(result.get("ticket_created", False)),
        ticketData=result.get("ticket_data"),
        confidence=float(result.get("confidence", 0.0)),
        sources=[str(c.get("source", c.get("id", ""))) for c in result.get("citations", []) if isinstance(c, dict)],
    )


@app.post("/api/invoke", response_model=InvokeResponse)
async def invoke(request: InvokeRequest, x_ai_agent_key: str | None = Header(default=None)):
    check_key(x_ai_agent_key)
    try:
        return await invoke_impl(request)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("invoke_request_failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await invoke_impl(InvokeRequest(
        message=request.message, customerId=request.customer_id, sessionId=request.session_id,
    ))
    return ChatResponse(session_id=request.session_id, response=result.response, intent="support",
        confidence=result.confidence, requires_human=not bool(result.confidence >= .60),
        actions_taken=result.suggestedActions, citations=[{"source": s} for s in result.sources])


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return await sessions.get(session_id)
