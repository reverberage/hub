#!/usr/bin/env python3
"""Validate model-catalog.json against schema."""

import json
import sys
from pathlib import Path

HUB_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = HUB_DIR / "data" / "model-catalog.json"

REQUIRED_MODEL_FIELDS = [
    "model_id", "tier", "priority", "family", "context_length",
    "thinking", "vision", "tool_use", "structured_output",
    "pricing", "quota", "skip",
]

REQUIRED_QUOTA_FIELDS = ["total", "unit", "expires"]


def validate() -> list[str]:
    errors: list[str] = []

    if not CATALOG_PATH.exists():
        errors.append(f"Catalog not found: {CATALOG_PATH}")
        return errors

    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    # Top-level fields
    if catalog.get("version") != 1:
        errors.append(f"Expected version=1, got {catalog.get('version')}")
    if not catalog.get("updated"):
        errors.append("Missing 'updated' date")
    if not catalog.get("expires"):
        errors.append("Missing 'expires' date")
    if not isinstance(catalog.get("models"), list):
        errors.append("'models' must be a list")
        return errors

    models = catalog["models"]
    if len(models) != 109:
        errors.append(f"Expected 109 models, got {len(models)}")

    llm_count = sum(1 for m in models if m.get("tier", 0) > 0)
    tts_count = sum(1 for m in models if m.get("tier", 0) == 0)
    if llm_count != 91:
        errors.append(f"Expected 91 LLM models, got {llm_count}")
    if tts_count != 18:
        errors.append(f"Expected 18 TTS models, got {tts_count}")

    seen_ids: set[str] = set()
    tier_counts: dict[int, int] = {}

    for i, model in enumerate(models):
        mid = model.get("model_id", f"<index {i}>")

        # Required fields
        for field in REQUIRED_MODEL_FIELDS:
            if field not in model:
                errors.append(f"[{mid}] Missing field: {field}")

        # Unique model_id
        if mid in seen_ids:
            errors.append(f"[{mid}] Duplicate model_id")
        seen_ids.add(mid)

        # Quota validation
        quota = model.get("quota", {})
        for field in REQUIRED_QUOTA_FIELDS:
            if field not in quota:
                errors.append(f"[{mid}] Missing quota field: {field}")

        # Tier tracking
        tier = model.get("tier", 0)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    # Summary
    if not errors:
        print(f"✅ Valid: {len(models)} models ({llm_count} LLM, {tts_count} TTS)")
        print(f"   Tiers: {dict(sorted(tier_counts.items()))}")

    return errors


if __name__ == "__main__":
    errors = validate()
    if errors:
        print(f"❌ {len(errors)} validation error(s):")
        for err in errors:
            print(f"   - {err}")
        sys.exit(1)
    sys.exit(0)
