from langchain.chat_models import init_chat_model
from src.config import get_settings


class MockModel:
    def with_structured_output(self, schema):
        async def invoke(messages):
            text = messages[-1]["content"].lower()
            if any(x in text for x in ("invoice", "bill", "charge", "payment")):
                return schema(intent="billing", confidence=0.92)
            if any(x in text for x in ("error", "exception", "bug", "failed", "not working")):
                return schema(intent="technical", confidence=0.90)
            if any(x in text for x in ("angry", "complaint", "manager", "human")):
                return schema(intent="escalation", confidence=0.90)
            return schema(intent="support", confidence=0.85)
        class Structured:
            ainvoke = staticmethod(invoke)
        return Structured()

    async def ainvoke(self, messages):
        return type("Msg", (), {"content": "Mock AI response: I can help with that. Please provide any additional details if needed."})()


def get_model():
    s = get_settings()
    if s.mock_llm:
        return MockModel()
    if s.model_provider == "anthropic" and not s.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required unless MOCK_LLM=true")
    if s.model_provider == "openai" and not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required unless MOCK_LLM=true")
    return init_chat_model(
        f"{s.model_provider}:{s.model_name}",
        temperature=0, timeout=45, max_tokens=2000, max_retries=3,
    )


######################################################################
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from src.config import get_settings


# keep your MockModel as-is


def get_model():
    s = get_settings()
    if s.mock_llm:
        return MockModel()

    if s.model_provider == "anthropic":
        if not s.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required unless MOCK_LLM=true")
        return init_chat_model(
            f"anthropic:{s.model_name}",
            temperature=0, timeout=45, max_tokens=2000, max_retries=3,
        )

    if s.model_provider == "openai":
        if not s.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required unless MOCK_LLM=true")
        return init_chat_model(
            f"openai:{s.model_name}",
            temperature=0, timeout=45, max_tokens=2000, max_retries=3,
        )

    if s.model_provider == "openrouter":
        if not s.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required unless MOCK_LLM=true")
        return ChatOpenAI(
            model=s.model_name,  # e.g. openrouter/free
            api_key=s.openrouter_api_key,
            base_url=s.openrouter_base_url,
            temperature=0,
            timeout=45,
            max_tokens=2000,
            max_retries=3,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": s.app_name,
            },
        )

    raise RuntimeError(f"Unsupported MODEL_PROVIDER: {s.model_provider}")
######################################################################