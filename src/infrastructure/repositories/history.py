"""Репозиторий для работы с историей запросов.

Этот модуль предоставляет методы для сохранения и получения истории лингвистических
запросов пользователей.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db import RequestHistory
from src.infrastructure.repositories.base import BaseRepository


class HistoryRepository(BaseRepository[RequestHistory]):
    """Репозиторий для управления историей запросов.

    Обеспечивает доступ к записям о выполненных анализах текста.
    """

    def __init__(self, session: AsyncSession):
        """Инициализирует репозиторий истории.

        Args:
            session: Асинхронная сессия базы данных.
        """
        super().__init__(RequestHistory, session)

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[RequestHistory]:
        """Получает историю запросов конкретного пользователя.

        Args:
            user_id: ID пользователя.
            skip: Количество пропускаемых записей.
            limit: Максимальное количество возвращаемых записей.

        Returns:
            List[RequestHistory]: Список записей истории, отсортированный по дате создания (сначала новые).
        """
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

