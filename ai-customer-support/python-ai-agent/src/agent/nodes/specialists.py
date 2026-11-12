import json
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from src.agent.model import get_model
from src.agent.mcp_tools import MCPToolRegistry
from src.agent.prompts import SPECIALIST_PROMPTS


async def build_specialist(intent: str):
    registry = MCPToolRegistry()
    if intent == "support":
        allowed = {"get_customer", "search_tickets", "get_ticket", "add_comment", "search_docs", "search_faq", "get_doc_context"}
        servers = ["backend", "rag"]
    elif intent == "billing":
        allowed = {"get_customer", "get_invoices", "get_invoice", "get_account_status"}
        servers = ["backend"]
    elif intent == "technical":
        allowed = {"get_customer", "search_tickets", "get_ticket", "search_docs", "hybrid_search", "find_similar_tickets", "get_doc_context", "list_issues", "get_issue"}
        servers = ["backend", "rag", "jira"]
    else:
        allowed = {"get_customer", "search_tickets", "get_ticket", "search_docs"}
        servers = ["backend", "rag"]
    tools = []
    for server in servers:
        tools.extend(await registry.discover(server, allowed))
    return create_agent(model=get_model(), tools=tools, system_prompt=SPECIALIST_PROMPTS.get(intent, SPECIALIST_PROMPTS["support"]))



class TicketDraft(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=100)
    priority: str = Field(min_length=1, max_length=50)


def _explicit_ticket_request(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in ("create a ticket", "open a ticket", "raise a ticket", "submit a ticket", "log a ticket"))

def _tool_payload(message):
    content = getattr(message, "content", "")
    if isinstance(content, list):
        text = "".join(str(x.get("text", x)) if isinstance(x, dict) else str(x) for x in content)
    else:
        text = str(content)
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_metadata(messages):
    ticket_created = False
    ticket_data = None
    citations = []
    for message in messages:
        name = getattr(message, "name", "") or ""
        payload = _tool_payload(message)
        if name == "create_ticket" and isinstance(payload, dict):
            ticket_created = True
            ticket_data = {k: payload.get(k) for k in ("title", "description", "category", "priority") if payload.get(k) is not None}
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict) and item.get("source"):
                    citations.append(item)
        elif isinstance(payload, dict) and payload.get("source"):
            citations.append(payload)
    return ticket_created, ticket_data, citations


async def run_specialist(state: dict):
    agent = await build_specialist(state["intent"])
    customer_context = (
        f"Customer ID: {state.get('customer_id', 'unknown')}. Use this customer_id for backend operations. "
        f"Customer email: {state.get('context_data', {}).get('customer_email')}. "
        f"Customer tier: {state.get('context_data', {}).get('customer_tier')}. "
        f"Conversation history: {state.get('conversation_history', [])}"
    )
    result = await agent.ainvoke({"messages": [
        {"role": "system", "content": customer_context},
        {"role": "user", "content": state["user_input"]},
    ]})
    messages = result.get("messages", [])
    final = messages[-1].content if messages else "No response generated."
    ticket_created, ticket_data, citations = _extract_metadata(messages)
    if not ticket_created and _explicit_ticket_request(state["user_input"]):
        draft_model = get_model().with_structured_output(TicketDraft)
        draft = await draft_model.ainvoke([
            {"role": "system", "content": "Create a concise support ticket draft from the user's request. Do not invent customer facts."},
            {"role": "user", "content": state["user_input"]},
        ])
        ticket_created = True
        ticket_data = draft.model_dump()
    return {
        "final_response": final,
        "actions_taken": [f"{state['intent']}_agent_completed"],
        "ticket_created": ticket_created,
        "ticket_data": ticket_data,
        "citations": citations,
    }


async def run_analysis(state: dict):
    # Analysis is deliberately skipped when running in mock mode; with a real
    # provider it provides a second-pass synthesis over the specialist answer.
    from src.config import get_settings
    if get_settings().mock_llm:
        return {"final_response": state["final_response"], "actions_taken": ["analysis_skipped_mock"]}
    agent = await build_specialist("analysis")
    result = await agent.ainvoke({"messages": [{"role": "user", "content": state["final_response"]}]})
    messages = result.get("messages", [])
    return {"final_response": messages[-1].content if messages else state["final_response"], "actions_taken": ["analysis_agent_completed"]}
