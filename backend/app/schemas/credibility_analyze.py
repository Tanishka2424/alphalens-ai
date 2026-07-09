from pydantic import BaseModel, Field

from app.schemas.clickbait import ClickbaitResponse
from app.schemas.credibility import ClassifierResponse
from app.schemas.emotional_language import EmotionalLanguageResponse
from app.schemas.source_reputation import SourceReputationResponse


class CredibilityAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    source_name: str | None = Field(default=None, description="Publisher name, if known.")
    url: str | None = Field(default=None, description="Article URL, if available.")


class CredibilityAnalyzeResponse(BaseModel):
    risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="0 = low risk, 1 = high risk. A weighted heuristic combination, not a statistical probability."
    )
    action_bucket: str = Field(..., description="'Reliable', 'Needs Verification', or 'High Risk'.")
    classifier: ClassifierResponse
    clickbait: ClickbaitResponse
    emotional_language: EmotionalLanguageResponse
    source_reputation: SourceReputationResponse
    disclaimer: str = Field(
        default=(
            "This is a heuristic risk indicator combining a fine-tuned classifier and "
            "linguistic/source signals. It is NOT a fact-verification or truth-certainty system."
        )
    )