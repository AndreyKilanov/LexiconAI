"""Модуль зависимостей для FastAPI.

Этот модуль содержит функции-провайдеры для внедрения зависимостей (Dependency Injection),
таких как репозитории и сервисы.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db import get_db
from src.infrastructure.repositories import (
    DictionaryRepository,
    HistoryRepository,
    UserRepository,
)
from src.services.linguistic import LinguisticService


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """Получает экземпляр репозитория пользователей.

    Args:
        session: Сессия базы данных.

    Returns:
        UserRepository: Экземпляр репозитория пользователей.
    """
    return UserRepository(session)


async def get_history_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HistoryRepository:
    """Получает экземпляр репозитория истории.

    Args:
        session: Сессия базы данных.

    Returns:
        HistoryRepository: Экземпляр репозитория истории.
    """
    return HistoryRepository(session)


async def get_dictionary_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DictionaryRepository:
    """Получает экземпляр репозитория словаря.

    Args:
        session: Сессия базы данных.

    Returns:
        DictionaryRepository: Экземпляр репозитория словаря.
    """
    return DictionaryRepository(session)


async def get_linguistic_service(
    dictionary_repo: Annotated[DictionaryRepository, Depends(get_dictionary_repository)],
    history_repo: Annotated[HistoryRepository, Depends(get_history_repository)],
) -> LinguisticService:
    """Получает экземпляр лингвистического сервиса.

    Args:
        dictionary_repo: Репозиторий словаря.
        history_repo: Репозиторий истории.

    Returns:
        LinguisticService: Экземпляр лингвистического сервиса.
    """
    return LinguisticService(dictionary_repo, history_repo)

