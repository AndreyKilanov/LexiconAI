"""Конфигурация базы данных.

Этот модуль настраивает SQLAlchemy: создает асинхронный движок, фабрику сессий
и определяет базовый класс для моделей.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""
    pass


engine = create_async_engine(
    settings.assemble_database_url,
    echo=settings.LOG_LEVEL == "DEBUG",
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий базы данных.

    Yields:
        AsyncSession: Экземпляр сессии SQLAlchemy.
    """
    async with async_session_factory() as session:
        yield session

