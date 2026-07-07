"""Provider factory — resolves provider names to instances."""

from __future__ import annotations

import os
from typing import Any

from rvrb_providers.base import ModelProvider
from rvrb_providers.fallback import FallbackProvider

# Registry: name → fully-qualified class path
_PROVIDER_REGISTRY: dict[str, str] = {
    "qwen": "rvrb_providers.qwen.QwenProvider",
    "openai": "rvrb_providers.openai.OpenAIProvider",
    "local": "rvrb_providers.local.LocalProvider",
    "fallback": "rvrb_providers.fallback.FallbackProvider",
}


def list_providers() -> list[str]:
    """Return the list of registered provider names (excluding fallback)."""
    return [name for name in _PROVIDER_REGISTRY if name != "fallback"]


def get_provider(name: str | None = None) -> ModelProvider:
    """Resolve a provider name to an instance.

    The name format is ``<provider_name>[:<model_override>]``.
    If ``name`` is ``None``, the ``RVRB_PROVIDER`` env var is read,
    defaulting to ``"qwen"``.

    =====================  ================================================
    Input                  Result
    =====================  ================================================
    ``None``               Read ``RVRB_PROVIDER`` env, default ``"qwen"``
    ``"qwen"``             ``QwenProvider()`` with env defaults
    ``"qwen:model-id"``    ``QwenProvider(model="model-id")``
    ``"fallback"``         Parse ``RVRB_FALLBACK_PROVIDERS`` env
    ``"fallback:anything"``  ``ValueError`` — fallback doesn't accept model
    ``"a:b:c"``            ``ValueError`` — too many parts
    ``"nonexistent"``      ``ValueError`` — unknown provider
    =====================  ================================================
    """
    resolved_name = (name or os.environ.get("RVRB_PROVIDER") or "qwen").strip().lower()

    # Parse colon-separated parts
    parts = resolved_name.split(":")
    if len(parts) > 2:
        raise ValueError(
            f"Invalid provider name: '{resolved_name}'. "
            f"Format: <provider> or <provider>:<model>"
        )

    provider_name = parts[0]
    model_override = parts[1] if len(parts) == 2 else None

    # Validate provider exists
    if provider_name not in _PROVIDER_REGISTRY:
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Available: {', '.join(list_providers())}"
        )

    # Fallback is special: it doesn't accept model override
    if provider_name == "fallback":
        if model_override is not None:
            raise ValueError(
                "Fallback provider does not accept a model override. "
                "Configure individual entries in RVRB_FALLBACK_PROVIDERS."
            )
        return _build_fallback()

    # Resolve provider class and instantiate
    return _build_provider(provider_name, model_override)


def _build_provider(provider_name: str, model_override: str | None) -> ModelProvider:
    """Import and instantiate a provider by registry name."""
    class_path = _PROVIDER_REGISTRY[provider_name]
    module_path, class_name = class_path.rsplit(".", 1)

    import importlib

    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)

    kwargs: dict[str, Any] = {}
    if model_override:
        kwargs["model"] = model_override

    return cls(**kwargs)


def _build_fallback() -> FallbackProvider:
    """Build a FallbackProvider from RVRB_FALLBACK_PROVIDERS env var."""
    raw = os.environ.get("RVRB_FALLBACK_PROVIDERS")
    if not raw or not raw.strip():
        raise ValueError(
            "RVRB_FALLBACK_PROVIDERS is not set. "
            "Set it to a comma-separated list of provider names."
        )
    entries = [entry.strip() for entry in raw.split(",") if entry.strip()]
    providers = [get_provider(entry) for entry in entries]
    return FallbackProvider(providers)
