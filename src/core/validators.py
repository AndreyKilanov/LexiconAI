"""Утилиты для валидации данных.

Этот модуль содержит классы и методы для проверки входных данных,
таких как корректность кириллических символов и форматы слов.
"""

import re


class WordValidator:
    """Класс для валидации текстовых данных (слов)."""

    _CYRILLIC_PATTERN = re.compile(r"^[а-яёА-ЯЁ\s-]+$")

    @classmethod
    def is_cyrillic(cls, text: str) -> bool:
        """Проверяет, содержит ли текст только кириллицу, пробелы и дефисы.

        Args:
            text: Текст для проверки.

        Returns:
            bool: True, если текст валиден, иначе False.
        """
        if not text:
            return False
        return bool(cls._CYRILLIC_PATTERN.match(text))

    @classmethod
    def validate_word(cls, text: str) -> None:
        """Валидирует текст и выбрасывает исключение при ошибке.

        Args:
            text: Текст для проверки.

        Raises:
            ValueError: Если текст содержит некириллические символы.
        """
        if not cls.is_cyrillic(text):
            raise ValueError(
                "Текст должен содержать только кириллические символы, пробелы или дефисы"
            )
