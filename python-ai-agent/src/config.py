from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "enterprise-ai-platform"
    environment: str = "dev"
    log_level: str = "INFO"
    #######################################################
    model_provider: str = "openrouter"
    model_name: str = "openrouter/free"

    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    embedding_model: str = "nvidia/nemotron-3-embed-1b:free"
    embedding_dimensions: int = 2048
    #######################################################
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    java_backend_url: str = "http://localhost:8080"
    java_api_key: str | None = None
    internal_api_key: str | None = None
    ai_agent_api_key: str | None = None
    mock_llm: bool = False

    redis_url: str = "redis://localhost:6379/0"
    session_ttl_seconds: int = 86400

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "enterprise_kb"

    backend_mcp_url: str = "http://localhost:8101/mcp"
    rag_mcp_url: str = "http://localhost:8102/mcp"
    slack_mcp_url: str = "http://localhost:8103/mcp"
    jira_mcp_url: str = "http://localhost:8104/mcp"

    slack_bot_token: str | None = None
    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = None

    rag_top_k: int = 5
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 120
    rag_enable_reranking: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "enterprise-ai-platform"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
