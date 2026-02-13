"""Цепочки LangChain для лингвистического анализа.

Этот модуль настраивает LLM и определяет цепочки (chains) для выполнения семантического
анализа слов, подбора синонимов и антонимов.
"""

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.core import WordAssociation, settings
from src.core.schemas import AssociationType
from src.core.exceptions import ExternalAPIError
from src.core.logger import get_logger

logger = get_logger(__name__)


class AnalysisResponse(BaseModel):
    """Схема структурированного ответа от LLM."""
    is_exists: bool = Field(description="True if the word exists in Russian dictionary, False otherwise.")
    synonyms: List[str] = Field(description="List of 5 synonyms (empty if word not exists).")
    antonyms: List[str] = Field(description="List of 5 antonyms (empty if word not exists).")


llm = ChatOpenAI(
    base_url=settings.llm.BASE_URL,
    api_key=settings.llm.API_KEY,
    model=settings.llm.MODEL,
    temperature=settings.llm.TEMPERATURE,
    max_retries=settings.llm.MAX_RETRIES,
    timeout=settings.llm.TIMEOUT,
)

structured_llm = llm.with_structured_output(AnalysisResponse, method="json_mode")

analysis_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Ты - эксперт-лингвист. Твоя задача - провести морфологический и семантический анализ слова. "
            "1. Проверь, существует ли слово в русском языке. Имена собственные считаются существующими. "
            "2. Если слово существует: подбери ровно 5 синонимов и 5 антонимов. "
            "3. Если слово НЕ существует (например, набор букв 'фдыва', 'ккк'): установи is_exists=false, а списки пустыми. "
            "4. Верни результат строго в JSON формате:\n"
            '{{\n'
            '  "is_exists": true/false,\n'
            '  "synonyms": ["слово1", "слово2"...],\n'
            '  "antonyms": ["слово1", "слово2"...]\n'
            '}}\n'
            "5. Убедись, что слова корректны и соответствуют части речи исходного слова.",
        ),
        ("user", "Проанализируй слово: {word}"),
    ]
)

analysis_chain = analysis_prompt | structured_llm


async def analyze_word(word: str) -> List[WordAssociation]:
    """Генерирует список из 10 ассоциаций (5 синонимов + 5 антонимов).

    Использует цепочку LangChain для обращения к LLM и получения
    структурированного результата.

    Args:
        word: Слово для анализа.

    Returns:
        List[WordAssociation]: Список из 10 ассоциаций.

    Raises:
        ExternalAPIError: При сетевых ошибках или ошибках на стороне LLM.
        ValueError: Если слово не найдено.
    """
    log = logger.bind(word=word)
    log.info("Invoking AI analysis chain")

    try:
        response: AnalysisResponse = await analysis_chain.ainvoke({"word": word})
        log.info(
            "Received response from LLM",
            is_exists=response.is_exists,
            synonyms_count=len(response.synonyms),
            antonyms_count=len(response.antonyms),
            full_response=response.model_dump()
        )
        
        if not response.is_exists:
            log.warning("Word not found by AI", word=word)
            raise ValueError(f"Слово '{word}' не найдено в русском языке.")

        associations = []
        for syn in response.synonyms:
            associations.append(WordAssociation(word=syn, type=AssociationType.SYNONYM))
        for ant in response.antonyms:
            associations.append(WordAssociation(word=ant, type=AssociationType.ANTONYM))

        return associations
    except ValueError as e:
        # Re-raise ValueError to be handled by service
        raise e
    except Exception as e:
        log.error("AI chain invocation failed", error=str(e), error_type=type(e).__name__)
        raise ExternalAPIError(
            message="Ошибка при обращении к AI сервису",
            details={"error": str(e), "word": word}
        ) from e


