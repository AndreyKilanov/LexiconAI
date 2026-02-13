"""Конфигурация приложения.

Этот модуль определяет настройки приложения, используя pydantic-settings для
загрузки конфигурации из переменных окружения и .env файла.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения.

    Attributes:
        APP_ENV: Окружение (development, production, testing).
        LOG_LEVEL: Уровень логирования.
        DATABASE_URL: URL для подключения к базе данных.
        TELEGRAM_BOT_TOKEN: Токен Telegram-бота.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # App
    APP_ENV: Literal["development", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "lexicon"
    DATABASE_URL: str | None = None

    # Ports
    APP_PORT: int = 8000

    @property
    def assemble_database_url(self) -> str:
        """Сборка URL подключения к базе данных.

        Returns:
            str: Полный URL для SQLAlchemy.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # LLM (Flattened for better env loading)
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: str
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_RETRIES: int = 2
    LLM_TIMEOUT: float = 60.0

    @property
    def llm(self) -> "LLMProxy":
        """Прокси для сохранения обратной совместимости с кодом, ожидающим settings.llm.attr."""
        return LLMProxy(self)


class LLMProxy:
    """Класс-прокси для имитации вложенных настроек LLM."""
    def __init__(self, settings: Settings):
        self.BASE_URL = settings.LLM_BASE_URL
        self.API_KEY = settings.LLM_API_KEY
        self.MODEL = settings.LLM_MODEL
        self.TEMPERATURE = settings.LLM_TEMPERATURE
        self.MAX_RETRIES = settings.LLM_MAX_RETRIES
        self.TIMEOUT = settings.LLM_TIMEOUT


settings = Settings()

