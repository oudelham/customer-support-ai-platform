from abc import ABC, abstractmethod
import io
from openai import AsyncOpenAI
from app.core.config import settings


class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        pass


class OpenAISTTProvider(STTProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename
        transcript = await self.client.audio.transcriptions.create(
            model=settings.STT_MODEL,
            file=audio_file,
            language="en",
            prompt="Beginner English learner practicing basic conversation.",
        )
        return transcript.text.strip()


def get_stt_provider() -> STTProvider:
    return OpenAISTTProvider()
