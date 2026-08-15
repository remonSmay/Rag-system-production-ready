from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Construct the path to the .env file in the project root directory.
    # The project root is two levels up from the current file's directory (src/helpers).
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str | None = None
    APP_VERSION: str | None = None

    FILE_ALLOWED_TYPES: list[str] | None = None
    FILE_MAX_SIZE: int = 0

    FILE_DEFAULT_CHUNK_SIZE: int = 51200  # 50 KB

    # Defaults match the docker-compose port mapping (27017:27017)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "mini_rag"
    GENERATION_BACKEND: str | None = None
    EMBEDDING_BACKEND: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_API_URL: str | None = None
    COHERE_API_KEY: str | None = None

    GENERATION_MODEL_ID: str | None = None
    EMBEDDING_MODEL_ID: str | None = None
    EMBEDDING_MODEL_SIZE: int | None = None
    INPUT_DEFAULT_MAX_CHARACTERS: int | None = None
    GENERATION_DEFAULT_MAX_TOKENS: int | None = None
    GENERATION_DEFAULT_TEMPERATURE: float | None = None
    VECTOR_DB_BACKEND: str | None = None
    VECTOR_DB_DISTANCE_METHOD: str | None = None
    VECTOR_DB_PATH: str = "qdrant_db"
    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"


@lru_cache
def get_settings() -> Settings:

    return Settings()
