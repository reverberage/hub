"""rvrb-providers: Provider-agnostic model interface for reverberage satellites."""

from __future__ import annotations

from rvrb_providers.base import ModelProvider
from rvrb_providers.factory import get_provider, list_providers
from rvrb_providers.models import (
    AllProvidersExhaustedError,
    ProviderError,
    QuotaExhaustedError,
    ToolCall,
    ToolResult,
)

__all__ = [
    "ModelProvider",
    "ProviderError",
    "QuotaExhaustedError",
    "AllProvidersExhaustedError",
    "ToolCall",
    "ToolResult",
    "get_provider",
    "list_providers",
]

__version__ = "0.1.0"
