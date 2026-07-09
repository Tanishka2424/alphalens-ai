from pydantic import BaseModel, Field


class ClickbaitRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)


class ClickbaitResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="0 = no clickbait signals, 1 = strong clickbait signals.")
    matched_phrases: list[str] = Field(..., description="Known clickbait phrases found in the text.")
    excessive_caps: bool = Field(..., description="Text has an unusually high ratio of ALL-CAPS words.")
    excessive_punctuation: bool = Field(..., description="Text has repeated '!' or '?' (e.g. '!!!' or '???').")