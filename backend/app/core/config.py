from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App metadata
    APP_NAME: str = "AlphaLens AI"
    APP_VERSION: str = "0.1.0"
    ENV: str = "development"  # development | production

    # Logging
    LOG_LEVEL: str = "INFO"

    # ML model identifiers (HuggingFace hub IDs)
    # FinBERT (Phase 1)
    FINBERT_MODEL_NAME: str = "ProsusAI/finbert"

    
    # Semantic retrieval (Phase 3)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "training/vector_store"
    # Inference device: "cpu" or "cuda"
    DEVICE: str = "cpu"
    
    # LLM for grounded explanations (any OpenAI-compatible provider, e.g. Groq).
    # No defaults on purpose: set all three in backend/.env.
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_NAME: str | None = None
    OPENAI_BASE_URL: str | None = None


# Singleton settings instance imported everywhere else
settings = Settings()
