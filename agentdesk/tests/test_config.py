import pytest

from config import Settings


def test_openai_provider_requires_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError):
        Settings()


def test_ollama_provider_allows_missing_openai_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = Settings()
    assert settings.llm_provider == "ollama"
