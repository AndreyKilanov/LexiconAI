"""Основной модуль приложения FastAPI.

Этот модуль инициализирует приложение FastAPI, настраивает логирование,
middleware, статические файлы и подключает роутеры.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.app.routers import linguistic, web
from src.app.templates import templates
from src.core import settings
from src.core.exceptions import AppError
from src.core.logger import get_logger, setup_logger

setup_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения.

    Args:
        app: Экземпляр приложения FastAPI.
    """
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="LexiconAI API",
    description="API для лингвистического сервиса на базе LangChain и LangGraph",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.APP_ENV == "development",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def index(request: Request):
    """Главная страница веб-интерфейса.

    Args:
        request: Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-страница index.html.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat")
async def chat(request: Request):
    """Страница чата (алиас для главной).

    Args:
        request: Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-страница index.html.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# Routers
app.include_router(linguistic.router)
app.include_router(web.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Обработчик известных исключений приложения.

    Args:
        request: Объект запроса.
        exc: Экземпляр AppError.

    Returns:
        JSONResponse: Ответ с деталями ошибки.
    """
    logger.error(
        "Application error occurred",
        path=request.url.path,
        error_code=exc.code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Обработчик всех непредвиденных исключений.

    Args:
        request: Объект запроса.
        exc: Экземпляр исключения.

    Returns:
        JSONResponse: Ответ с кодом 500.
    """
    logger.exception(
        "Unhandled exception occurred",
        path=request.url.path,
        error_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "Произошла внутренняя ошибка сервера",
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации данных (Pydantic).

    Args:
        request: Объект запроса.
        exc: Экземпляр исключения валидации.

    Returns:
        JSONResponse: Ответ с кодом 422 и списком ошибок.
    """
    logger.error(
        "Validation error occurred",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Ошибка валидации входных данных",
                "details": exc.errors(),
            }
        },
    )


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса.

    Returns:
        dict: Статус сервиса и текущее окружение.
    """
    return {"status": "ok", "env": settings.APP_ENV}

