from __future__ import annotations

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from config import Settings


def get_llm(settings: Settings):
    if settings.llm_provider == "openai":
        return ChatOpenAI(model=settings.model_name, temperature=settings.temperature)

    return ChatOllama(
        model=settings.model_name,
        temperature=settings.temperature,
        base_url=settings.ollama_base_url,
    )
