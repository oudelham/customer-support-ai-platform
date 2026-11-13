from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    def get_chat_model(self, temperature: float = 0.4) -> BaseChatModel:
        pass

    @abstractmethod
    def get_structured_model(self, schema: Type[T], temperature: float = 0.1):
        pass


class OpenAILLMProvider(LLMProvider):
    def get_chat_model(self, temperature: float = 0.4) -> BaseChatModel:
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )

    def get_structured_model(self, schema: Type[T], temperature: float = 0.1):
        model = self.get_chat_model(temperature=temperature)
        return model.with_structured_output(schema)


def get_llm_provider() -> LLMProvider:
    return OpenAILLMProvider()
