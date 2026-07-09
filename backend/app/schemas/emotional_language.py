from pydantic import BaseModel, Field


class EmotionalLanguageRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)


class EmotionalLanguageResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="0 = neutral tone, 1 = heavily loaded/sensational tone.")
    matched_words: list[str] = Field(..., description="Emotionally loaded words found in the text.")
    density: float = Field(..., description="Fraction of total words that were emotionally loaded.")