# Frontend ↔ Java compatibility report

## Fixed mismatches

| Area | Original pasted frontend | Java backend | Result |
|---|---|---|---|
| API base | `localhost:8080/api/v1` | default server port 8080 | Compatible |
| Login | `/auth/login` | `/auth/login` | Compatible after camelCase DTOs |
| Refresh | expected full AuthResponse | returns `{accessToken}` | Adapted |
| Logout | `/auth/logout` | `/auth/logout` | Compatible |
| Register | `/auth/register` | not implemented | Removed from UI/service |
| Current user | `/auth/me` | not implemented | Removed from active flow |
| Chat | `/chat` | `/api/v1/chat` | Compatible |
| Chat request | `message`, `session_id` | `message`, `sessionId` | Adapted to camelCase |
| Chat response | snake_case | camelCase | Adapted |
| Tickets | `/tickets...` | `/api/v1/tickets...` | Compatible |
| AI review | `/tickets/pending/ai` | same | Compatible |
| Approve | `approved_by` | `notes` | Adapted |
| Reject | `reason` | `reason`, `sendNotification` | Adapted |
| IDs | strings | Java `Long` | Adapted to numbers |
| AI service URL | browser variable | Java owns AI-agent call | Not used by browser |

## End-to-end ownership

The browser talks only to Spring Boot. Spring Boot calls the Python AI agent. This preserves the enterprise-backend boundary and keeps AI credentials/server-side.
