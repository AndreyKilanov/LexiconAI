"""Модуль для создания клавиатур Telegram-бота.

Этот модуль содержит функции для генерации различных типов клавиатур
(Reply и Inline), используемых в интерфейсе бота.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from src.core.schemas import RequestType


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает главную клавиатуру с типами запросов.

    Returns:
        ReplyKeyboardMarkup: Объект главной клавиатуры.
    """
    buttons = [
        [
            KeyboardButton(text="Синонимы"),
            KeyboardButton(text="Антонимы"),
        ],
        [KeyboardButton(text="Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_retry_keyboard(word: str, request_type: RequestType) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для повтора запроса.

    Args:
        word: Слово, для которого нужно повторить запрос.
        request_type: Тип запроса (синоним/антоним).

    Returns:
        InlineKeyboardMarkup: Объект инлайн-клавиатуры.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="🔄 Попробовать еще раз",
                callback_data=f"retry:{request_type}:{word}",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

