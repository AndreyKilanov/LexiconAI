#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}>>> LexiconAI start script initiated...${NC}"

# Функция для отправки уведомления в Telegram (опционально)
send_telegram_notification() {
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
        local message="$1"
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$ADMIN_CHAT_ID" \
            -d text="$message" \
            -d parse_mode="HTML" > /dev/null
    fi
}

echo -e "${BLUE}>>> Checking database migrations...${NC}"
mkdir -p src/infrastructure/db/migrations/versions
ls -ld src/infrastructure/db/migrations/versions

if [ "$RUN_MODE" == "app" ]; then
    # Только основной сервис генерирует миграции, если их нет
    if [ -z "$(ls -A src/infrastructure/db/migrations/versions/*.py 2>/dev/null)" ]; then
        echo -e "${BLUE}>>> No migrations found. Initializing (RUN_MODE=app)...${NC}"
        python -m alembic revision --autogenerate -m "Initial migration"
        echo -e "${GREEN}>>> Initial migration created.${NC}"
    fi
else
    # Другие сервисы (bot) ждут появления файлов миграций от основного сервиса
    echo -e "${BLUE}>>> Waiting for migrations to be initialized by app service...${NC}"
    RETRY_COUNT=0
    while [ -z "$(ls -A src/infrastructure/db/migrations/versions/*.py 2>/dev/null)" ] && [ $RETRY_COUNT -lt 30 ]; do
        sleep 2
        RETRY_COUNT=$((RETRY_COUNT+1))
    done
fi

# Все сервисы пытаются применить миграции (alembic сам разрулит конкуренцию)
echo -e "${BLUE}>>> Applying migrations...${NC}"
python -m alembic upgrade head
echo -e "${GREEN}>>> Migrations applied successfully.${NC}"

# Сообщение в ТГ перед запуском (если настроено)
NOTIF_MSG="🚀 <b>LexiconAI</b>: Сервис успешно запущен и готов к работе!"
send_telegram_notification "$NOTIF_MSG"

# Выбор команды запуска на основе переменной RUN_MODE
if [ "$RUN_MODE" == "bot" ]; then
    echo -e "${GREEN}>>> Starting Telegram Bot...${NC}"
    exec python -m src.bot.main
else
    echo -e "${GREEN}>>> Starting API Application...${NC}"
    exec python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips "*"
fi
