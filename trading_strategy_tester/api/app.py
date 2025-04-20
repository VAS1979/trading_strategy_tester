""" Точка входа в приложение """

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from trading_strategy_tester.api.routers import router
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Trading Strategy Tester", description="API для тестирования торговых стратегий.", version="1.0.0")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации запросов.
    Логирует ошибку и возвращает ответ с деталями ошибки.
    """

    logger.error("Ошибка валидации: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"detail": "Ошибка валидации запроса", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик исключений.
    Логирует неожиданные ошибки и возвращает сообщение об ошибке.
    """
    logger.exception("Произошла непредвиденная ошибка: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Произошла непредвиденная ошибка на сервере"},
    )


if __name__ == "__main__":
    logger.info("Запуск сервера Uvicorn")
    uvicorn.run(app, host="127.0.0.1", port=8080)
