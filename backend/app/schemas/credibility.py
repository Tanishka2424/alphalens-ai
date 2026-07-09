"""
Schema for the raw classifier signal only (Real/Fake + confidence).

This is NOT the final credibility score endpoint - that combines this
classifier's output with clickbait detection, emotional-language scoring,
and source reputation lookup into one score + action bucket. Those come
next; this is just the fine-tuned model wrapped as its own service, same
as how sentiment.py exposes FinBERT on its own before anything else uses it.
"""
from enum import Enum

from pydantic import BaseModel, Field


class ClassifierLabel(str, Enum):
    REAL = "Real"
    FAKE = "Fake"


class ClassifierRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="News headline or article text to classify.",
    )


class ClassifierResponse(BaseModel):
    label: ClassifierLabel = Field(..., description="Predicted class.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: dict[str, float] = Field(
        ..., description="Raw probability distribution across both classes."
    )
    inference_time_ms: float