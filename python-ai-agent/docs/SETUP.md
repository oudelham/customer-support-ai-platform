# Setup

## 1. Infrastructure

```bash
cp .env.example .env
docker compose up -d redis qdrant
```

## 2. Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Knowledge base

Set `OPENAI_API_KEY`, then:

```bash
python -m src.rag.indexing knowledge
```

## 4. Java backend

Set:

```text
JAVA_BACKEND_URL=http://localhost:8081
JAVA_API_KEY=...
```

The Java backend should expose the `/api/v1/...` endpoints described in the
portfolio specification.

## 5. MCP servers

Run each on its configured port.

## 6. AI API

```bash
uvicorn src.api.main:app --reload --port 8080
```

## 7. Example request

```bash
curl -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "demo-001",
    "channel": "api",
    "customer_id": "1",
    "message": "Why is my production authentication failing?"
  }'
```
