"""Shared test fixtures."""
import pytest
from pathlib import Path


@pytest.fixture
def agent_script():
    """Path to main agent script."""
    return Path(__file__).parent.parent / "main.py"


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-mock")
