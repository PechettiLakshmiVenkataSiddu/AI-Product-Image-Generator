from __future__ import annotations

import logging
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Literal["openai", "ollama"] = Field(default="openai", alias="LLM_PROVIDER")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/agentdesk.log", alias="LOG_FILE")

    workspace_dir: str = Field(default="workspace", alias="WORKSPACE_DIR")
    max_iterations: int = Field(default=8, alias="MAX_ITERATIONS")
    temperature: float = Field(default=0.0, alias="TEMPERATURE")

    @model_validator(mode="after")
    def validate_provider_keys(self) -> "Settings":
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Set LLM_PROVIDER=ollama to run locally without an API key."
            )
        return self

    @property
    def workspace_path(self) -> Path:
        return (BASE_DIR / self.workspace_dir).resolve()

    @property
    def log_file_path(self) -> Path:
        return (BASE_DIR / self.log_file).resolve()


def setup_logging(settings: Settings) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    console.setFormatter(console_formatter)

    settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)
    rotating_file = RotatingFileHandler(
        settings.log_file_path,
        maxBytes=1_048_576,
        backupCount=3,
        encoding="utf-8",
    )
    rotating_file.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    )
    rotating_file.setFormatter(file_formatter)

    root_logger.addHandler(console)
    root_logger.addHandler(rotating_file)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.workspace_path.mkdir(parents=True, exist_ok=True)
    return settings
