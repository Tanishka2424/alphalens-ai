from pydantic import BaseModel, Field


class SimilarArticlesRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of similar articles to return.")


class SimilarArticleResult(BaseModel):
    title: str
    snippet: str = Field(..., description="First ~300 characters of the matched article.")
    source: str | None = None
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="1 = identical meaning, 0 = unrelated.")


class SimilarArticlesResponse(BaseModel):
    results: list[SimilarArticleResult]