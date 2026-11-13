# Customer Support Frontend

React + TypeScript frontend adapted to the supplied Java Spring Boot backend.

## Compatibility decisions

The original pasted frontend specification had several mismatches with the Java backend. This implementation fixes them:

- Java base URL defaults to `http://localhost:8080/api/v1`.
- `/chat` maps to Java `POST /api/v1/chat`.
- `/chat/history/:sessionId` maps to Java `GET /api/v1/chat/history/{sessionId}`.
- Ticket endpoints use Java's camelCase JSON DTOs.
- Login expects Java `LoginResponse`: `accessToken`, `refreshToken`, `user`.
- Refresh expects Java `RefreshRequest`: `refreshToken` and returns `{ accessToken }`.
- The frontend does not call `/auth/register` or `/auth/me` because those endpoints are not present in the supplied Java backend.
- AI review approval sends `{ notes?: string }`, matching Java `ApproveTicketRequest`.
- Rejection sends `{ reason, sendNotification }`, matching Java `RejectTicketRequest`.
- Customer/ticket IDs are numeric because the Java entities use `Long`.
- The frontend never calls the Python AI service directly. The intended flow is browser -> Java -> Python AI agent.

## Run

```bash
cp .env.example .env
npm install
npm start
```

For the integrated Docker stack, if Java is exposed on a different host port, set:

```env
REACT_APP_API_URL=http://localhost:8081/api/v1
```

## Demo login

```text
john@aisupport.com
password
```

The password is from the demo seed in the Java project and should be changed for real deployment.

## Important backend limitation

The current Java comment endpoint accepts a comment but does not persist it. The UI therefore confirms submission but does not expect the comment to appear after reload.

The current Java `/auth/logout` is also stateless; the frontend clears its local token after calling it.

## AI architecture

```text
React
  -> Java Spring Boot /api/v1/chat
      -> Python FastAPI /api/invoke
          -> LangGraph
              -> MCP / RAG / LLM
      <- AI response
  <- Java ChatResponse
```
