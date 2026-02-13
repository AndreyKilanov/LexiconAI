"""Репозиторий для работы с данными пользователей.

Этот модуль предоставляет методы для управления информацией о пользователях
в базе данных, включая поиск по Telegram ID.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db import User
from src.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для управления информацией о пользователях.

    Обеспечивает доступ к профилям пользователей, взаимодействующих с ботом.
    """

    def __init__(self, session: AsyncSession):
        """Инициализирует репозиторий пользователей.

        Args:
            session: Асинхронная сессия базы данных.
        """
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получает пользователя по его Telegram ID.

        Args:
            telegram_id: Идентификатор пользователя в Telegram.

        Returns:
            Optional[User]: Найденный пользователь или None.
        """
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

