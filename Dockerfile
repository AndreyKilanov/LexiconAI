# Базовый образ с Python 3.12
FROM python:3.12-slim AS builder

# Настройки переменных окружения для Python и Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app"

# Добавление Poetry в PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Установка системных зависимостей для сборки
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Финальный образ для запуска
FROM python:3.12-slim AS runtime

# Настройки переменных окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Установка системных библиотек, необходимых во время выполнения (например, libpq для Postgres)
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -s /bin/bash -m app

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Копирование исходного кода
COPY --chown=app:app . .

# Копирование скрипта запуска и установка прав
COPY --chown=app:app start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Создаем папку для миграций и устанавливаем права (важно для Docker Volumes)
RUN mkdir -p /app/src/infrastructure/db/migrations/versions && \
    chown -R app:app /app/src/infrastructure/db/migrations/versions

# Переключение на пользователя app
USER app

# Параметры по умолчанию
ENV APP_PORT=8000 \
    PYTHONPATH=/app

# Экспонирование порта
EXPOSE ${APP_PORT}

# Команда запуска через скрипт
ENTRYPOINT ["/app/start.sh"]
