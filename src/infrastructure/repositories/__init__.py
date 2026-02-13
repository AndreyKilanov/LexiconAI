"""Пакет с репозиториями приложения."""

from src.infrastructure.repositories.base import BaseRepository
from src.infrastructure.repositories.dictionary import DictionaryRepository
from src.infrastructure.repositories.history import HistoryRepository
from src.infrastructure.repositories.user import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "HistoryRepository",
    "DictionaryRepository",
]
