"""Конфигурация шаблонов Jinja2.

Этот модуль инициализирует объект Jinja2Templates для использования в приложении.
"""

from pathlib import Path
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
