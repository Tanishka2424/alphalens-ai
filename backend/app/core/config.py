"""
Centralized application configuration.

All environment-dependent values live here and nowhere else in the codebase.
This is what makes the app config-driven instead of hardcoded, and it's the
first thing an interviewer will ask about if they see os.environ scattered
through the code instead.
"""
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

    # Credibility classifier (Phase 2) - local fine-tuned checkpoint, not a
    # Hugging Face hub model. Path is relative to the backend/ working dir.
    CREDIBILITY_MODEL_PATH: str = "training/checkpoints/credibility_classifier"
    # Semantic retrieval (Phase 3)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "training/vector_store"
    # Inference device: "cpu" or "cuda"
    DEVICE: str = "cpu"


# Singleton settings instance imported everywhere else
settings = Settings()
