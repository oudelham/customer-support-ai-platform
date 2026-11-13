# Lingo2U (MVP)

A simplified, beginner-focused (CEFR A1-A2) spoken English practice web app.

## Tech Stack
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Zustand (No Next.js)
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL
- **AI Orchestration:** LangGraph + LangChain (No MCP in MVP)

## Quick Start
1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. Run:
   ```bash
   docker compose up --build
   ```
3. Open `http://localhost:5173` in your browser (`http://localhost:8000/docs` for API docs).
4. Run backend tests:
   ```bash
   docker compose exec backend pytest
   ```
