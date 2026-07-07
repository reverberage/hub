"""Tests for rvrb_verify.models — pure Pydantic, zero fixtures."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from rvrb_verify.models import Claim, Evidence, Source, Verdict, VerdictEnum


class TestVerdictEnum:
    def test_values(self) -> None:
        assert VerdictEnum.TRUE.value == "true"
        assert VerdictEnum.FALSE.value == "false"
        assert VerdictEnum.UNCERTAIN.value == "uncertain"
        assert VerdictEnum.OPINION.value == "opinion"
        assert VerdictEnum.UNVERIFIABLE.value == "unverifiable"

    def test_membership(self) -> None:
        assert "true" in VerdictEnum._value2member_map_
        assert "false" in VerdictEnum._value2member_map_


class TestClaim:
    def test_basic(self) -> None:
        c = Claim(text="The sky is blue")
        assert c.text == "The sky is blue"
        assert c.domain == "fact-check"

    def test_custom_domain(self) -> None:
        c = Claim(text="Legal claim", domain="legal")
        assert c.domain == "legal"

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValidationError):
            Claim(text="")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError):
            Claim(text="   \t  \n  ")

    def test_json_roundtrip(self) -> None:
        c = Claim(text="Test claim")
        data = c.model_dump_json()
        restored = Claim.model_validate_json(data)
        assert restored.text == c.text
        assert restored.domain == c.domain


class TestSource:
    def test_basic(self) -> None:
        s = Source(title="Example", url="https://example.com", snippet="Some text")
        assert s.title == "Example"
        assert s.url == "https://example.com"
        assert s.snippet == "Some text"

    def test_default_retrieved_at(self) -> None:
        s = Source()
        assert isinstance(s.retrieved_at, datetime)
        assert s.retrieved_at.tzinfo is not None

    def test_json_roundtrip(self) -> None:
        s = Source(title="T", url="https://u.com", snippet="Snippet")
        data = s.model_dump_json()
        restored = Source.model_validate_json(data)
        assert restored.title == s.title
        assert restored.url == s.url
        assert restored.retrieved_at == s.retrieved_at


class TestEvidence:
    def test_basic(self) -> None:
        e = Evidence(supports=True, reasoning="It's obvious")
        assert e.supports is True
        assert e.reasoning == "It's obvious"
        assert e.sources == []

    def test_with_sources(self) -> None:
        src = Source(title="Wiki", url="https://wiki.com")
        e = Evidence(supports=True, reasoning="Source says", sources=[src])
        assert len(e.sources) == 1
        assert e.sources[0].title == "Wiki"

    def test_default_supports(self) -> None:
        e = Evidence(reasoning="Reason")
        assert e.supports is True


class TestVerdict:
    def test_basic(self) -> None:
        v = Verdict(
            claim="The sky is blue",
            verdict=VerdictEnum.TRUE,
            confidence=0.95,
            summary="Rayleigh scattering",
        )
        assert v.claim == "The sky is blue"
        assert v.verdict == VerdictEnum.TRUE
        assert v.confidence == 0.95
        assert v.summary == "Rayleigh scattering"
        assert v.evidence == []
        assert v.model_used == ""

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Verdict(
                claim="x",
                verdict=VerdictEnum.FALSE,
                confidence=1.5,  # too high
            )

    def test_confidence_zero(self) -> None:
        v = Verdict(claim="x", verdict=VerdictEnum.UNCERTAIN, confidence=0.0)
        assert v.confidence == 0.0

    def test_confidence_one(self) -> None:
        v = Verdict(claim="x", verdict=VerdictEnum.TRUE, confidence=1.0)
        assert v.confidence == 1.0

    def test_negative_confidence_raises(self) -> None:
        with pytest.raises(ValidationError):
            Verdict(claim="x", verdict=VerdictEnum.FALSE, confidence=-0.1)

    def test_with_evidence(self) -> None:
        e = Evidence(supports=False, reasoning="Counter-evidence")
        v = Verdict(
            claim="x",
            verdict=VerdictEnum.FALSE,
            confidence=0.8,
            evidence=[e],
        )
        assert len(v.evidence) == 1
        assert v.evidence[0].reasoning == "Counter-evidence"

    def test_with_model_used(self) -> None:
        v = Verdict(
            claim="x",
            verdict=VerdictEnum.TRUE,
            confidence=0.9,
            model_used="qwen3.7-plus",
        )
        assert v.model_used == "qwen3.7-plus"

    def test_json_roundtrip(self) -> None:
        v = Verdict(
            claim="Test claim",
            verdict=VerdictEnum.TRUE,
            confidence=0.85,
            summary="Test summary",
        )
        data = v.model_dump_json()
        restored = Verdict.model_validate_json(data)
        assert restored.claim == v.claim
        assert restored.verdict == v.verdict
        assert restored.confidence == v.confidence
        assert restored.summary == v.summary
