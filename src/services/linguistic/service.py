"""Сервис для лингвистического анализа.

Этот модуль содержит основную бизнес-логику для обработки слов,
включая взаимодействие с репозиториями и графом AI.
"""

from typing import Any, Dict

from src.core import ProcessingStatus, WordAssociation
from src.core.exceptions import AppError
from src.core.logger import get_logger
from src.infrastructure.repositories import DictionaryRepository, HistoryRepository
from src.services.linguistic.graph import app_graph

logger = get_logger(__name__)


class LinguisticService:
    """Сервис для выполнения лингвистических операций.

    Оркестрирует процесс анализа слова: поиск в кэше, вызов AI и сохранение истории.

    Attributes:
        dictionary_repo: Репозиторий для работы с кэшем слов.
        history_repo: Репозиторий для сохранения истории запросов.
        logger: Логгер сервиса.
    """

    def __init__(
        self,
        dictionary_repo: DictionaryRepository,
        history_repo: HistoryRepository,
    ):
        """Инициализирует лингвистический сервис.

        Args:
            dictionary_repo: Репозиторий словаря.
            history_repo: Репозиторий истории.
        """
        self.dictionary_repo = dictionary_repo
        self.history_repo = history_repo
        self.logger = logger

    async def analyze_word(self, word: str, source: str = "web") -> Dict[str, Any]:
        """Проводит полный анализ слова.

        Алгоритм работы:
        1. Проверяет наличие слова в кэше (БД).
        2. При отсутствии в кэше — вызывает AI-граф для генерации ассоциаций.
        3. Сохраняет полученный результат в кэш.
        4. Создает запись в истории запросов.

        Args:
            word: Слово для анализа.
            source: Источник запроса (web, telegram, api).

        Returns:
            Dict[str, Any]: Словарь с результатами анализа:
                - result: Список WordAssociation или None.
                - error: Сообщение об ошибке или None.
                - status: Статус обработки (ProcessingStatus).
        """
        word = word.strip().lower()
        log = self.logger.bind(word=word, source=source)
        log.info("Starting word analysis")

        try:
            # 1. Проверка кэша
            cached_entry = await self.dictionary_repo.get_by_word(word)
            if cached_entry:
                log.info("Cache hit for word")
                associations_data = cached_entry.associations.get("items", [])
                associations = [WordAssociation(**item) for item in associations_data]

                await self.history_repo.create(
                    source=source,
                    original_text=word,
                )

                return {
                    "result": associations,
                    "error": None,
                    "status": ProcessingStatus.COMPLETED
                }

            # 2. Запрос к AI
            log.info("Cache miss, calling AI graph")
            inputs = {"word": word, "result": None, "error": None}
            result_state = await app_graph.ainvoke(inputs)

            result_data = result_state.get("result")
            error_data = result_state.get("error")

            if error_data:
                log.error("AI graph returned error", error=error_data)

            # 3. Сохранение в кэш
            if result_data:
                log.info("Saving results to cache")
                json_data = {"items": [item.model_dump() for item in result_data]}
                await self.dictionary_repo.upsert(word, json_data)

            # 4. Логирование
            await self.history_repo.create(
                source=source,
                original_text=word,
            )

            return {
                "result": result_data,
                "error": error_data,
                "status": ProcessingStatus.COMPLETED if not error_data else ProcessingStatus.FAILED
            }

        except ValueError as e:
            log.warning("Validation error or unknown word", error=str(e))
            return {
                "result": None,
                "error": str(e),
                "status": ProcessingStatus.FAILED
            }
        except AppError as e:
            log.error("Known app error during word analysis", error_code=e.code, message=e.message)
            return {
                "result": None,
                "error": e.message,
                "status": ProcessingStatus.FAILED
            }
        except Exception as e:
            log.exception("Unexpected error during word analysis")
            return {
                "result": None,
                "error": "Произошла внутренняя ошибка при анализе слова",
                "status": ProcessingStatus.FAILED
            }

