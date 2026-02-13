"""Пакет с исключениями приложения."""

from src.core.exceptions.base import (
    AppError,
    DatabaseError,
    ExternalAPIError,
    InfrastructureError,
    LinguisticError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "AppError",
    "InfrastructureError",
    "DatabaseError",
    "NotFoundError",
    "ValidationError",
    "ExternalAPIError",
    "LinguisticError",
]

