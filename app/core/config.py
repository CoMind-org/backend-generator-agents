import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str | None = os.getenv("MONGO_URI")
    database_name: str | None = os.getenv("DATABASE_NAME")
    github_token: str | None = os.getenv("GITHUB_TOKEN")
    github_endpoint: str = os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.github.ai/inference")
    github_model: str = os.getenv("GITHUB_MODEL", "openai/gpt-4o")
    model_path: str = os.getenv("MODEL_PATH", "models")
    gemini_token: str | None = os.getenv("GEMINI_TOKEN")


settings = Settings()


def require_mongo_settings() -> None:
    if not settings.mongo_uri:
        raise ValueError("MONGO_URI is missing in .env")
    if not settings.database_name:
        raise ValueError("DATABASE_NAME is missing in .env")


def require_github_settings() -> None:
    if not settings.github_token:
        raise ValueError("GITHUB_TOKEN is missing in .env")


def require_gemini_settings() -> None:
    if not settings.gemini_token:
        raise ValueError("GEMINI_TOKEN is missing in .env")
