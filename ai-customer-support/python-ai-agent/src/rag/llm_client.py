from openai import AsyncOpenAI
from src.config import get_settings


def get_openai_compatible_client() -> AsyncOpenAI:
    s = get_settings()
    # Prefer OpenRouter when no OpenAI key
    if s.openrouter_api_key:
        return AsyncOpenAI(
            api_key=s.openrouter_api_key,
            base_url=s.openrouter_base_url,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": s.app_name,
            },
        )
    if s.openai_api_key:
        return AsyncOpenAI(api_key=s.openai_api_key)
    raise RuntimeError("Set OPENROUTER_API_KEY or OPENAI_API_KEY")