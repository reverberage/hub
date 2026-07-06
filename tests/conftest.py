"""Shared fixtures for hub tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for scaffold tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)
