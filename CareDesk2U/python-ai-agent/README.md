# Enterprise AI Integration Platform — Python AI Layer

This repository implements the Python side of the **Enterprise AI Integration Platform**.
The existing Java/Spring Boot service remains the system of record for customers, tickets,
and billing.

## Implemented components

- LangGraph stateful orchestrator with intent routing and specialist agents.
- MCP client layer that discovers tools from remote MCP servers and exposes them to agents.
- Four MCP servers:
  - backend/data access → wraps the existing Java REST API
  - RAG/knowledge base → Qdrant search and document retrieval
  - Slack integration
  - Jira integration
- RAG ingestion: PDF/DOCX/Markdown/text → chunking → embeddings → Qdrant.
- Semantic retrieval, BM25 fallback, hybrid ranking, optional cross-encoder reranking.
- Redis session storage.
- FastAPI `/chat`, `/health`, and `/sessions/{id}` endpoints.
- Structured JSON logging.
- Basic evaluation hooks and unit tests.
- Docker Compose for local development.

## Current architecture

```text
                    +----------------------+
                    |       FastAPI        |
                    |       /chat          |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | LangGraph Orchestrator|
                    | intent -> specialist |
                    +----------+-----------+
                               |
             +-----------------+------------------+
             |                 |                  |
             v                 v                  v
        Support Agent    Billing Agent      Technical Agent
             |                 |                  |
             +-----------------+------------------+
                               |
                               v
                         MCP Client Layer
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
   Backend MCP           RAG MCP             Slack/Jira MCP
          |                    |                    |
          v                    v                    v
   Java Spring API          Qdrant             External APIs
```

## Run locally

1. Copy `.env.example` to `.env`.
2. Start infrastructure:

```bash
docker compose up -d redis qdrant
```

3. Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Start the four MCP servers in separate terminals:

```bash
python -m src.mcp_servers.backend_server
python -m src.mcp_servers.rag_server
python -m src.mcp_servers.slack_server
python -m src.mcp_servers.jira_server
```

5. Start the API:

```bash
uvicorn src.api.main:app --reload --port 8080
```

6. Ingest documents:

```bash
python -m src.rag.indexing ./knowledge
```

The Java service is expected at `JAVA_BACKEND_URL` and must expose the endpoints described
by the original project specification.

## Important

The MCP SDK is intentionally pinned to the current v2 line. MCP v2 is the current stable
Python SDK line; the server/client implementation here uses `MCPServer`, `@mcp.tool()`,
`Client(...)`, and Streamable HTTP. See the official MCP SDK documentation for deployment
and security hardening before exposing these servers publicly.
