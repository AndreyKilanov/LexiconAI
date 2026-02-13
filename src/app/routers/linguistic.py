"""Роутер для лингвистических операций.

Этот модуль определяет API-эндпоинты для анализа текста, поиска синонимов и антонимов
с использованием кэширования в базе данных и обработки через LangGraph.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.dependencies import (
    get_linguistic_service,
)
from src.core import (
    LinguisticRequestBase,
    LinguisticResponse,
    ProcessingStatus,
)
from src.core.logger import get_logger
from src.services.linguistic import LinguisticService

router = APIRouter(prefix="/api", tags=["api"])
logger = get_logger(__name__)


@router.post("/analyze", response_model=LinguisticResponse)
async def analyze_text(
    request: LinguisticRequestBase,
    service: Annotated[LinguisticService, Depends(get_linguistic_service)],
):
    """Полный лингвистический анализ слова (синонимы + антонимы).

    Args:
        request: Данные запроса с текстом для анализа.
        service: Лингвистический сервис.

    Returns:
        LinguisticResponse: Результат лингвистического анализа.
    """
    word = request.text.strip().lower()
    logger.info("API analysis request", word=word)

    result = await service.analyze_word(word, source="api")

    if result["status"] == ProcessingStatus.FAILED:
        return LinguisticResponse(
            request_id=uuid.uuid4(),
            original_text=word,
            status=ProcessingStatus.FAILED,
            error=result["error"]
        )

    return LinguisticResponse(
        request_id=uuid.uuid4(),
        original_text=word,
        status=ProcessingStatus.COMPLETED,
        result=result["result"],
    )

