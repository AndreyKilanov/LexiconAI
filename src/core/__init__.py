"""Ядро приложения: конфигурация, схемы и базовые компоненты."""

from src.core.config import settings
from src.core.schemas import (
    LinguisticRequestBase,
    LinguisticResponse,
    ProcessingStatus,
    RequestType,
    WordAssociation,
)

__all__ = [
    "settings",
    "ProcessingStatus",
    "RequestType",
    "WordAssociation",
    "LinguisticRequestBase",
    "LinguisticResponse",
]
