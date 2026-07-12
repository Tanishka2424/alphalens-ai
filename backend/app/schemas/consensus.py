from pydantic import BaseModel, Field


class ConsensusRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20)


class RelatedArticleSentiment(BaseModel):
    title: str
    sentiment: str
    similarity_score: float


class ConsensusResponse(BaseModel):
    verdict: str = Field(
        ..., description="'Consensus', 'Partial Agreement', 'Conflict', or 'Insufficient Coverage'."
    )
    explanation: str
    user_claim_sentiment: str | None = None
    related_articles: list[RelatedArticleSentiment]
    exaggeration_flag: bool = Field(
        ..., description="True if the user's text is notably more emotionally loaded than the related coverage."
    )
    method: str = Field(default="rule_based_fallback", description="'rule_based_fallback' or 'llm_assisted'.")