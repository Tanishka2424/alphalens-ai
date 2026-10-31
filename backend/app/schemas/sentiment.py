"""
Request/response schemas for the sentiment analysis endpoint.

Kept separate from the service logic and the route handler so the API
contract is explicit and versionable independent of implementation details.
"""
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SentimentLabel(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class SentimentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Financial news headline or article text to analyze.",
        examples=["Fed signals possible rate cuts as inflation cools further."],
    )

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("text must contain at least 10 non-whitespace characters")
        return v


class SentimentResponse(BaseModel):
    label: SentimentLabel = Field(..., description="Predicted sentiment class.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model softmax score for the predicted label. Not a calibrated probability.",
    )
    scores: dict[str, float] = Field(
        ...,
        description="Softmax scores for all three classes. They sum to about 1 but are not calibrated probabilities.",
    )
    inference_time_ms: float = Field(
        ..., description="Time taken for model inference, in milliseconds."
    )