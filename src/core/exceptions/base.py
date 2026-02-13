"""Базовые исключения приложения.

Этот модуль определяет иерархию исключений, используемых в приложении для
обработки ошибок различной природы: от ошибок валидации до проблем с инфраструктурой.
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Базовый класс для всех исключений приложения.

    Attributes:
        message: Человекочитаемое описание ошибки.
        code: Код ошибки для программной обработки.
        status_code: HTTP статус-код.
        details: Дополнительные детали ошибки.
    """

    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует базовое исключение.

        Args:
            message: Описание ошибки.
            code: Символьный код ошибки.
            status_code: HTTP статус-код.
            details: Словарь с подробностями.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class InfrastructureError(AppError):
    """Ошибки инфраструктурного уровня (БД, Redis и т.д.)."""

    def __init__(
        self,
        message: str,
        code: str = "infrastructure_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует ошибку инфраструктуры."""
        super().__init__(message, code, status_code, details)


class DatabaseError(InfrastructureError):
    """Ошибки при работе с базой данных."""

    def __init__(
        self,
        message: str,
        code: str = "database_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует ошибку базы данных."""
        super().__init__(message, code, status_code, details)


class NotFoundError(AppError):
    """Ошибка: ресурс не найден."""

    def __init__(
        self,
        message: str,
        code: str = "not_found",
        status_code: int = 404,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует ошибку 'Не найдено'."""
        super().__init__(message, code, status_code, details)


class ValidationError(AppError):
    """Ошибка валидации данных."""

    def __init__(
        self,
        message: str,
        code: str = "validation_error",
        status_code: int = 422,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует ошибку валидации."""
        super().__init__(message, code, status_code, details)


class ExternalAPIError(InfrastructureError):
    """Ошибки при взаимодействии с внешними API (OpenAI, Telegram и т.д.)."""

    def __init__(
        self,
        message: str,
        code: str = "external_api_error",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует ошибку внешнего API."""
        super().__init__(message, code, status_code, details)


class LinguisticError(AppError):
    """Логические ошибки лингвистического сервиса."""

    def __init__(
        self,
        message: str,
        code: str = "linguistic_logic_error",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Инициализирует лингвистическую ошибку."""
        super().__init__(message, code, status_code, details)

