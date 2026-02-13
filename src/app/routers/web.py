"""Роутер для веб-интерфейса.

Этот модуль содержит эндпоинты для обработки запросов от фронтенда (HTMX),
возвращая HTML-фрагменты для динамического обновления страниц.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request

from src.app.dependencies import get_linguistic_service
from src.app.templates import templates
from src.core.logger import get_logger
from src.core.validators import WordValidator
from src.services.linguistic import LinguisticService

router = APIRouter(prefix="/web", tags=["web"])
logger = get_logger(__name__)


@router.post("/analyze")
async def analyze_web(
    request: Request,
    text: Annotated[str, Form()],
    service: Annotated[LinguisticService, Depends(get_linguistic_service)],
):
    """Обработка запроса из веб-формы (HTMX).

    Анализирует слово через лингвистический сервис и возвращает HTML-фрагмент
    с результатами.

    Args:
        request: Объект запроса FastAPI.
        text: Текст для анализа, полученный из формы.
        service: Лингвистический сервис.

    Returns:
        TemplateResponse: HTML-фрагмент partials/result.html.
    """
    logger.info("Web analysis request", text=text)

    if not WordValidator.is_cyrillic(text):
        return templates.TemplateResponse(
            "partials/result.html",
            {
                "request": request,
                "original_text": text,
                "error": "Пожалуйста, используйте только кириллицу.",
                "result": None,
            },
        )

    result = await service.analyze_word(text, source="web")
    context = {
        "request": request,
        "original_text": text,
        "result": result.get("result"),
        "error": result.get("error"),
        "status": result.get("status"),
    }

    return templates.TemplateResponse("partials/result.html", context)

