from pydantic import BaseModel, Field

from app.schemas.clickbait import ClickbaitResponse
from app.schemas.emotional_language import EmotionalLanguageResponse
from app.schemas.source_reputation import SourceReputationResponse


class CredibilityAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    source_name: str | None = Field(default=None, description="Publisher name, if known.")
    url: str | None = Field(default=None, description="Article URL, if available.")


class CredibilityAnalyzeResponse(BaseModel):
    clickbait: ClickbaitResponse
    emotional_language: EmotionalLanguageResponse
    source_context: SourceReputationResponse
    disclaimer: str = Field(
        default=(
            "These are writing-style and source-context signals only. "
            "They do not show whether a claim is true or false."
        )
    )