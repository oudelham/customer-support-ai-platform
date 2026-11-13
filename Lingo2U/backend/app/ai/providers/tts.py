from abc import ABC, abstractmethod
import base64
from openai import AsyncOpenAI
from app.core.config import settings


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize_base64(self, text: str, slow: bool = False) -> str:
        pass


class OpenAITTSProvider(TTSProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def synthesize_base64(self, text: str, slow: bool = False) -> str:
        response = await self.client.audio.speech.create(
            model=settings.TTS_MODEL,
            voice=settings.TTS_VOICE,
            input=text,
            speed=0.75 if slow else 0.92,
            response_format="mp3",
        )
        audio_bytes = response.content
        return base64.b64encode(audio_bytes).decode("utf-8")


def get_tts_provider() -> TTSProvider:
    return OpenAITTSProvider()
