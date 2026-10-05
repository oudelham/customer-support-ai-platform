# Customer Support Backend

Spring Boot 3.2 / Java 21 enterprise backend for the customer-support AI platform.

## Responsibility split

**Java/Spring Boot**
- Authentication/JWT
- Customer, ticket and invoice system of record
- Chat persistence
- Redis conversation cache
- AI-agent HTTP integration
- AI-generated ticket creation and officer approval workflow
- Audit logging
- Slack MCP and email integration boundary
- REST API for React

**Python**
- LangGraph agent orchestration
- LLM calls
- RAG/Qdrant
- MCP tool servers
- Agent evaluation/guardrails

## Run locally

```bash
cp .env.example .env
docker compose up -d postgres redis
./mvnw.sh spring-boot:run
```

Or install Maven and run:

```bash
mvn spring-boot:run
```

The API starts on `http://localhost:8080`.

## Build

```bash
mvn clean package
docker compose build backend
docker compose up
```

## Demo credentials

The Flyway demo migration creates:
- `john@aisupport.com`
- `officer@aisupport.com`

The seed password is `password` for the bcrypt value used by the demo migration. Change/remove demo credentials before any real deployment.

## Python integration contract

Java calls:

```http
POST ${AI_AGENT_URL}/api/invoke
Content-Type: application/json
X-Request-ID: <uuid>
```

Request:

```json
{
  "message": "I can't login",
  "customerId": "1",
  "customerEmail": "john@aisupport.com",
  "customerTier": "pro",
  "sessionId": "sess_abc123",
  "conversationHistory": [],
  "context": {}
}
```

Expected response:

```json
{
  "response": "I found a similar issue. Try resetting your password.",
  "suggestedActions": ["reset_password", "create_ticket"],
  "ticketCreated": true,
  "ticketData": {
    "title": "Login problem",
    "description": "Customer cannot log in",
    "category": "technical",
    "priority": "high"
  },
  "confidence": 0.92,
  "sources": ["Login troubleshooting"]
}
```

## Main endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/chat`
- `GET /api/v1/chat/history/{sessionId}`
- `GET /api/v1/tickets`
- `GET /api/v1/tickets/{ticketId}`
- `POST /api/v1/tickets`
- `PUT /api/v1/tickets/{ticketId}`
- `POST /api/v1/tickets/{ticketId}/approve`
- `POST /api/v1/tickets/{ticketId}/reject`
- `POST /api/v1/tickets/{ticketId}/comments`
- `GET /api/v1/tickets/pending/ai`
- `GET /api/v1/customers/{customerId}`
- `PUT /api/v1/customers/{customerId}`
- `GET /api/v1/customers/{customerId}/invoices`
- `GET /actuator/health`

## Important production hardening

This is a portfolio/reference implementation, not a claim that every production control is complete. Before production:
1. Replace wildcard CORS with the real frontend origin.
2. Move secrets to AWS Secrets Manager/SSM.
3. Use a strong JWT secret and preferably asymmetric signing/rotation.
4. Implement refresh-token persistence/revocation rather than stateless logout.
5. Add role checks to every officer/admin operation.
6. Add request rate limiting at ALB/API Gateway and/or Redis.
7. Add distributed tracing and structured JSON logs.
8. Add an idempotency key for AI ticket creation.
9. Replace demo email/Slack boundaries with authenticated integrations.
10. Add integration/contract tests against the real Python agent and MCP services.
11. Use a ticket-number sequence instead of `count()+1` under concurrent load.
12. Add pagination/authorization tests and database migration tests.
