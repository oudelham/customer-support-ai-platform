# Python AI Architecture

## Responsibilities

### Java
The existing Spring Boot service remains responsible for:
- customer records
- tickets
- invoices
- business rules
- transactional persistence
- enterprise REST APIs

### Python
The Python service is responsible for:
- LLM interaction
- agent orchestration
- intent routing
- RAG
- MCP client/server integration
- session orchestration
- AI evaluation
- AI-specific observability

## Why MCP

MCP provides a protocol boundary between the agent and enterprise capabilities.
The agent does not need to know how Jira, Slack, or the Java API is implemented.
It discovers typed tools and invokes them through MCP.

## Safety boundary

Read operations can be exposed directly to agents. Write operations should be
protected by authorization and, for consequential actions, human approval.

## Production path

Local Docker Compose is the development target. The service is stateless except
for Redis/Qdrant and can be packaged as a container for ECS Fargate.
