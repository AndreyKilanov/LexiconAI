"""Базовый репозиторий для работы с базой данных.

Этот модуль предоставляет абстрактный базовый класс для реализации паттерна "Репозиторий",
обеспечивая стандартные операции CRUD через SQLAlchemy.
"""

from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DatabaseError
from src.core.logger import get_logger
from src.infrastructure.db import Base

logger = get_logger(__name__)
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый асинхронный репозиторий.

    Предоставляет общие методы для работы с моделями БД.

    Attributes:
        model: Класс модели SQLAlchemy, с которой работает репозиторий.
        session: Асинхронная сессия базы данных.
        logger: Настроенный логгер с контекстом модели.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Инициализирует репозиторий.

        Args:
            model: Класс SQLAlchemy модели.
            session: Асинхронная сессия.
        """
        self.model = model
        self.session = session
        self.logger = logger.bind(model=model.__name__)

    async def get(self, id: UUID) -> Optional[ModelType]:
        """Получает одну запись по её ID.

        Args:
            id: Уникальный идентификатор записи.

        Returns:
            Optional[ModelType]: Найденная модель или None.
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получает список всех записей с поддержкой пагинации.

        Args:
            skip: Количество пропускаемых записей.
            limit: Максимальное количество возвращаемых записей.

        Returns:
            List[ModelType]: Список найденных моделей.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Создает и сохраняет новую запись в БД.

        Args:
            **kwargs: Поля и значения для создания модели.

        Returns:
            ModelType: Созданный экземпляр модели.

        Raises:
            DatabaseError: При ошибке на стороне базы данных.
        """
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
            self.logger.info("Created instance", **kwargs)
            return instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to create instance", error=str(e), **kwargs)
            raise DatabaseError(message="Ошибка при создании записи в БД", details={"error": str(e)}) from e

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Обновляет существующую запись.

        Args:
            instance: Экземпляр модели для обновления.
            **kwargs: Поля и их новые значения.

        Returns:
            ModelType: Обновленный экземпляр модели.

        Raises:
            DatabaseError: При ошибке на стороне базы данных.
        """
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
            self.logger.info("Updated instance", id=instance.id, **kwargs)
            return instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to update instance", id=instance.id, error=str(e), **kwargs)
            raise DatabaseError(message="Ошибка при обновлении записи в БД", details={"error": str(e)}) from e

    async def delete(self, instance: ModelType) -> None:
        """Удаляет запись из БД.

        Args:
            instance: Экземпляр модели для удаления.

        Raises:
            DatabaseError: При ошибке на стороне базы данных.
        """
        try:
            instance_id = instance.id
            await self.session.delete(instance)
            await self.session.commit()
            self.logger.info("Deleted instance", id=instance_id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to delete instance", id=instance.id, error=str(e))
            raise DatabaseError(message="Ошибка при удалении записи из БД", details={"error": str(e)}) from e

