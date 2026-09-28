"""Doc cau hinh chung tu .env."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    GEMINI_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""  # nhieu key, cach nhau boi dau phay, de xoay vong khi het quota
    GROQ_API_KEY: str = ""
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "labor_law"
    LLM_MODEL: str = "gemini-3.8-flash"
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    @property
    def gemini_api_keys(self) -> list[str]:
        keys = [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]
        if keys:
            return keys
        return [self.GEMINI_API_KEY] if self.GEMINI_API_KEY else []


settings = Settings()
