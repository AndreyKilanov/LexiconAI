"""Основной модуль Telegram-бота.

Этот модуль инициализирует Telegram-бота, настраивает диспетчер,
подключает роутеры и запускает опрос (polling) серверов Telegram.
"""

import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from src.bot.handlers import router
from src.core import settings
from src.core.exceptions import AppError
from src.core.logger import get_logger, setup_logger

setup_logger()
logger = get_logger(__name__)


async def main():
    """Запуск Telegram-бота.

    Инициализирует бота и диспетчер, удаляет вебхуки и запускает бесконечный
    цикл получения обновлений.
    """
    logger.info("Starting bot...")

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    @dp.errors()
    async def global_error_handler(event: types.ErrorEvent):
        """Обработка всех ошибок в Telegram-боте.

        Логирует возникшее исключение и пытается отправить пользователю
        сообщение об ошибке, если это возможно.

        Args:
            event: Событие ошибки aiogram.
        """
        exception = event.exception
        update = event.update

        chat_id = None
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id

        log = logger.bind(
            update_id=update.update_id,
            error_type=type(exception).__name__,
            chat_id=chat_id
        )

        if isinstance(exception, AppError):
            log.warning("App error in bot", message=exception.message, code=exception.code)
            error_text = f"⚠ {exception.message}"
        else:
            log.exception("Unhandled error in bot")
            error_text = "⚠ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."

        if chat_id:
            try:
                await bot.send_message(chat_id, error_text)
            except Exception as e:
                log.error("Failed to send error message to user", send_error=str(e))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")

