# Customer Support AI Platform — Java + Python + React

This is the audited, compatibility-fixed end-to-end stack.

## Architecture

React/TypeScript → Spring Boot/Java → Python/LangGraph → MCP tools → Java/Qdrant/Slack/Jira

The browser only talks to Java. Java owns authentication, tickets, customers, invoices and chat persistence. Python owns the AI orchestration and MCP/RAG layer.

## Run the complete stack

```bash
cp .env.example .env
# Keep MOCK_LLM=true for a provider-free smoke test.
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Java API: http://localhost:8081
- Python AI health: http://localhost:8001/health

Demo login:

- `john@example.com` / `password`
- `officer@example.com` / `password`

## Real LLM

Set `MOCK_LLM=false` and provide `OPENAI_API_KEY`, or switch `MODEL_PROVIDER` to `anthropic` and provide `ANTHROPIC_API_KEY`.

## Main compatibility contract

### React → Java

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/chat`
- `GET /api/v1/chat/history/{sessionId}`
- `GET /api/v1/tickets`
- `GET /api/v1/tickets/{ticketId}`
- `POST /api/v1/tickets/{ticketId}/comments` with `{ "text": "..." }`
- `GET /api/v1/tickets/pending/ai`
- `POST /api/v1/tickets/{ticketId}/approve` with `{ "notes": "..." }`
- `POST /api/v1/tickets/{ticketId}/reject` with `{ "reason": "...", "sendNotification": false }`

### Java → Python

`POST http://ai-service:8080/api/invoke` with `X-AI-Agent-Key`.

Python returns `response`, `suggestedActions`, `ticketCreated`, `ticketData`, `confidence`, and `sources` exactly as the Java DTO expects.

### Python → Java

Backend MCP uses `X-Internal-API-Key` and the audited paths under `/api/v1`.

### Slack

The Python Slack service exposes normal MCP at `/mcp`. It also exposes an internal `/tools/send_message` compatibility adapter used only by the Java approval workflow, protected by `X-Internal-API-Key`.

## Important behavior

Explicit ticket requests are drafted by the Python agent and persisted as `pending` tickets by Java. Officer approval changes the ticket to `open` and triggers the Slack/email notification boundary.
