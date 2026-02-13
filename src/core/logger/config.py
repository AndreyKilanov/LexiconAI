"""Конфигурация логирования.

Этот модуль настраивает структурированное логирование с использованием библиотеки structlog,
обеспечивая различный формат вывода для разработки (консоль) и продакшена (JSON).
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from src.core.config import settings


def setup_logger() -> None:
    """Настройка structlog для проекта.

    Конфигурирует процессоры, обработчики и форматирование в зависимости
    от переменной окружения APP_ENV.
    """
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.APP_ENV == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.dict_tracebacks)
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.LOG_LEVEL)),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL,
    )


def get_logger(name: str | None = None) -> Any:
    """Получение экземпляра логгера.

    Args:
        name: Имя логгера (обычно передается __name__).

    Returns:
        Any: Настроенный экземпляр логгера structlog.
    """
    return structlog.get_logger(name)
