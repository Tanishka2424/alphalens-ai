from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.retrieval import SimilarArticleResult


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=10)


class CitedStatement(BaseModel):
    text: str
    evidence_ids: list[str] = Field(
        ..., min_length=1, description="IDs of the evidence items this statement relies on."
    )


class ExplainResponse(BaseModel):
    status: Literal["grounded", "insufficient_evidence"]
    statements: list[CitedStatement] = Field(default_factory=list)
    uncertainty: str = Field(..., description="What the evidence does not show.")
    evidence: list[SimilarArticleResult] = Field(default_factory=list)
    differences: list[str] = Field(
        default_factory=list,
        description="Differences between the claim and the cited headline/snippet, found by code (not the LLM).",
    )
    dropped_statements: int = Field(
        default=0,
        description="Statements removed because they cited unknown IDs or contained numbers found nowhere in the claim or cited text.",
    )
    disclaimer: str = Field(
        default=(
            "Statements are limited to what the cited articles say. Related articles are context, "
            "not confirmation. This tool does not decide whether a claim is true or false."
        )
    )