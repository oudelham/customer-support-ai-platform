from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://Lingo2U:Lingo2U_dev@localhost:5432/Lingo2U"
    SYNC_DATABASE_URL: str = "postgresql+psycopg://Lingo2U:Lingo2U_dev@localhost:5432/Lingo2U"
    JWT_SECRET_KEY: str = "dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    STT_MODEL: str = "whisper-1"
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "alloy"
    DAILY_TURN_CAP: int = 50


settings = Settings()
