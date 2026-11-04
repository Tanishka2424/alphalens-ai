from pydantic import BaseModel, Field


class SimilarArticlesRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of related articles to return.")


class SimilarArticleResult(BaseModel):
    article_id: str = Field(..., description="Stable ID of the article in the vector store.")
    title: str
    snippet: str = Field(..., description="First ~300 characters of the matched article.")
    source: str | None = Field(default=None, description="Dataset or publisher label, only if known.")
    url: str | None = Field(default=None, description="Original article URL, only if known.")
    published_at: str | None = Field(default=None, description="Publication time, only if known.")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Embedding cosine similarity. NOT a probability and NOT proof of relevance or agreement.",
    )


class SimilarArticlesResponse(BaseModel):
    results: list[SimilarArticleResult]
    excluded_duplicates: int = Field(
        default=0, description="Self-matches or near-duplicates removed from the results."
    )