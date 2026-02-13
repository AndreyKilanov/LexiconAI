"""Репозиторий для работы со словарем слов.

Этот модуль реализует специфичные для словаря операции, включая поиск по слову
и операцию upsert (создание или обновление) для кэширования результатов анализа.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DatabaseError
from src.infrastructure.db import WordDictionary
from src.infrastructure.repositories.base import BaseRepository


class DictionaryRepository(BaseRepository[WordDictionary]):
    """Репозиторий для управления кэшем слов и их ассоциаций.

    Наследует базовые операции и расширяет их функционалом для работы с уникальными словами.
    """

    def __init__(self, session: AsyncSession):
        """Инициализирует репозиторий словаря.

        Args:
            session: Асинхронная сессия базы данных.
        """
        super().__init__(WordDictionary, session)

    async def get_by_word(self, word: str) -> Optional[WordDictionary]:
        """Находит запись в словаре по конкретному слову.

        Args:
            word: Слово для поиска.

        Returns:
            Optional[WordDictionary]: Найденная запись или None.
        """
        stmt = select(self.model).where(self.model.word == word)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert(self, word: str, associations: dict) -> WordDictionary:
        """Создает новую запись или обновляет существующую, если слово уже есть.

        Args:
            word: Слово для сохранения.
            associations: Словарь с ассоциациями (синонимы, антонимы).

        Returns:
            WordDictionary: Созданный или обновленный экземпляр модели.

        Raises:
            DatabaseError: При ошибке выполнения операции в базе данных.
        """
        try:
            stmt = (
                insert(self.model)
                .values(word=word, associations=associations)
                .on_conflict_do_update(
                    index_elements=[self.model.word],
                    set_={"associations": associations},
                )
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            instance = result.scalars().one()
            self.logger.info("Upserted word", word=word)
            return instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to upsert word", word=word, error=str(e))
            raise DatabaseError(message="Ошибка при сохранении слова в БД", details={"error": str(e)}) from e

