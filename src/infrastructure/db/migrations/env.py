"""Конфигурация окружения Alembic.

Этот модуль используется Alembic для запуска миграций. Он настраивает соединение
с базой данных и определяет метаданные моделей для автоматической генерации миграций.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.config import settings
from src.infrastructure.db.base import Base
from src.infrastructure.db.models import RequestHistory, User, WordDictionary  # noqa

# Объект конфигурации Alembic
config = context.config

# Настройка логирования на основе файла конфигурации
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме.

    Конфигурирует контекст только с использованием URL, без создания движка.
    Это позволяет генерировать SQL-скрипты без прямого подключения к БД.
    """
    url = settings.assemble_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Непосредственный запуск миграций через соединение.

    Args:
        connection: Активное соединение с базой данных.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме.

    Создает асинхронный движок и связывает соединение с контекстом Alembic.
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = settings.assemble_database_url
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

