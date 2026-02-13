"""Схемы данных и перечисления.

Этот модуль содержит Pydantic-модели и Enum-классы, используемые для валидации
данных, взаимодействия с API и внутреннего представления объектов.
"""

from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.validators import WordValidator


class RequestType(str, Enum):
    """Типы лингвистических запросов."""
    SYNONYM = "synonym"
    ANTONYM = "antonym"
    DEFINITION = "definition"
    EXAMPLES = "examples"


class ProcessingStatus(str, Enum):
    """Статусы обработки запроса."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    pass


class User(UserBase):
    """Схема пользователя с системными полями."""
    id: UUID = Field(default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)


class LinguisticRequestBase(BaseModel):
    """Базовая схема лингвистического запроса."""
    text: str
    request_type: RequestType
    language: str = "ru"

    @field_validator("text")
    @classmethod
    def validate_cyrillic(cls, v: str) -> str:
        """Проверяет, что текст содержит только кириллические символы.

        Args:
            v: Текст для проверки.

        Returns:
            str: Проверенный текст.

        Raises:
            ValueError: Если текст содержит некириллические символы.
        """
        WordValidator.validate_word(v)
        return v


class AssociationType(str, Enum):
    """Типы ассоциаций слов."""
    SYNONYM = "synonym"
    ANTONYM = "antonym"


class WordAssociation(BaseModel):
    """Схема ассоциации слова."""
    word: str
    type: AssociationType


class LinguisticResponse(BaseModel):
    """Схема ответа на лингвистический запрос."""
    request_id: UUID
    original_text: str
    request_type: RequestType = Field(default=RequestType.SYNONYM)
    status: ProcessingStatus
    result: Optional[List[WordAssociation]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


