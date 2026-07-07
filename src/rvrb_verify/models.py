"""Pydantic models for claim verification."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class VerdictEnum(StrEnum):
    """Possible verdicts for a claim."""

    TRUE = "true"
    FALSE = "false"
    UNCERTAIN = "uncertain"
    OPINION = "opinion"
    UNVERIFIABLE = "unverifiable"


class Claim(BaseModel):
    """A claim to be verified."""

    text: str = Field(..., min_length=1, description="The claim text")
    domain: str = Field(default="fact-check", description="Verification domain")

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Claim text cannot be empty")
        return v


class Source(BaseModel):
    """A source used as evidence for a claim."""

    title: str = Field(default="", description="Source title")
    url: str = Field(default="", description="Source URL")
    snippet: str = Field(default="", description="Relevant excerpt")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this source was retrieved",
    )


class Evidence(BaseModel):
    """Evidence for or against a claim."""

    supports: bool = Field(default=True, description="Does this support the claim?")
    reasoning: str = Field(default="", description="Why this evidence is relevant")
    sources: list[Source] = Field(default_factory=list, description="Supporting sources")


class Verdict(BaseModel):
    """Final verdict on a claim."""

    claim: str = Field(..., description="The original claim text")
    verdict: VerdictEnum = Field(..., description="The verdict")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the verdict (0.0-1.0)"
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="Evidence supporting the verdict"
    )
    summary: str = Field(default="", description="Human-readable explanation")
    model_used: str = Field(default="", description="Model used for judgment")
