"""Граф обработки лингвистических запросов.

Этот модуль определяет структуру и логику графа LangGraph для управления
процессом анализа текста.
"""

from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from src.core import WordAssociation
from src.services.linguistic.chains import analyze_word


class GraphState(TypedDict):
    """Состояние графа обработки запроса.

    Attributes:
        word: Исходное слово для анализа.
        result: Список полученных ассоциаций.
        error: Сообщение об ошибке, если анализ не удался.
    """
    word: str
    result: List[WordAssociation] | None
    error: str | None


# Узлы графа
async def process_analysis(state: GraphState) -> Dict[str, Any]:
    """Обрабатывает запрос на полный анализ слова.

    Вызывает цепочку анализа для получения ассоциаций и обновляет состояние графа.

    Args:
        state: Текущее состояние графа.

    Returns:
        Dict[str, Any]: Обновленные поля состояния (result или error).
    """
    try:
        result = await analyze_word(state["word"])
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# Построение графа
workflow = StateGraph(GraphState)

# Добавляем узлы
workflow.add_node("analyzer", process_analysis)

# Определяем переходы
workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", END)

# Компилируем граф
app_graph = workflow.compile()

