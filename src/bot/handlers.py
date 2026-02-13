"""Обработчики сообщений Telegram-бота.

Этот модуль определяет логику обработки команд и текстовых сообщений,
получаемых от пользователей в Telegram.
"""

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold

from src.core import ProcessingStatus
from src.core.logger import get_logger
from src.core.validators import WordValidator
from src.infrastructure.db import async_session_factory
from src.infrastructure.repositories import DictionaryRepository, HistoryRepository
from src.services.linguistic import LinguisticService

router = Router()
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start.

    Приветствует пользователя и кратко описывает возможности бота.

    Args:
        message: Объект сообщения Telegram.
    """
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Я LexiconAI бот. Отправь мне любое слово, и я найду для него синонимы и антонимы."
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help.

    Предоставляет справку по использованию бота.

    Args:
        message: Объект сообщения Telegram.
    """
    await message.answer(
        "Просто напиши слово, например 'счастье', и я проведу его анализ."
    )


@router.message(F.text)
async def analyze_message_text(message: types.Message):
    """Обработка текстового сообщения как запроса на анализ.

    Выполняет поиск синонимов и антонимов для присланного слова, используя
    лингвистический сервис.

    Args:
        message: Объект сообщения Telegram с текстом.
    """
    word = message.text.strip()
    if not WordValidator.is_cyrillic(word):
        await message.answer("Пожалуйста, введите слово на кириллице без посторонних символов.")
        return

    if len(word) > 50:
        await message.answer("Слишком длинное слово. Попробуйте что-то короче.")
        return

    status_msg = await message.answer(f"Анализирую слово {hbold(word)}...", parse_mode="HTML")

    try:
        async with async_session_factory() as session:
            dictionary_repo = DictionaryRepository(session)
            history_repo = HistoryRepository(session)
            service = LinguisticService(dictionary_repo, history_repo)
            response = await service.analyze_word(word, source="telegram")

        if response["status"] == ProcessingStatus.FAILED:
            await status_msg.edit_text(f"Произошла ошибка: {response['error']}", parse_mode="HTML")
            return

        result = response["result"]
        if not result:
            await status_msg.edit_text("Ничего не найдено.", parse_mode="HTML")
            return

        synonyms = list(dict.fromkeys([item.word for item in result if item.type == 'synonym']))
        antonyms = list(dict.fromkeys([item.word for item in result if item.type == 'antonym']))

        text_parts = [f"Результат для: {hbold(word)}\n"]

        if synonyms:
            text_parts.append(f"✅ {hbold('Синонимы')}:")
            text_parts.append(", ".join(synonyms))
            text_parts.append("")

        if antonyms:
            text_parts.append(f"❌ {hbold('Антонимы')}:")
            text_parts.append(", ".join(antonyms))

        await status_msg.edit_text("\n".join(text_parts), parse_mode="HTML")

    except Exception as e:
        logger.error(
            "Error handling message",
            user_id=message.from_user.id,
            username=message.from_user.username,
            word=word,
            error=str(e),
            exc_info=True
        )
        await status_msg.edit_text("Произошла внутренняя ошибка сервера.")

