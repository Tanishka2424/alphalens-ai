from pydantic import BaseModel, Field


class SourceReputationRequest(BaseModel):
    source_name: str | None = Field(
        default=None, description="Publisher name if known, e.g. 'Reuters'."
    )
    url: str | None = Field(
        default=None, description="Article URL, if available - domain will be extracted."
    )


class SourceReputationResponse(BaseModel):
    tier: str = Field(
        ..., description="'Known outlet' (on our curated list) or 'Not in our list'. Not a reliability judgment."
    )
    resolved_domain: str | None = Field(default=None, description="Domain extracted from the URL, if provided.")
    matched_via: str | None = Field(
        default=None, description="Whether the match came from 'url', 'source_name', or None."
    )