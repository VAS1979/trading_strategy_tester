""" Точка входа в приложение """

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from trading_strategy_tester.api.routers import router
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Strategy Tester",
    description="API для тестирования торговых стратегий.",
    version="1.0.0"
)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
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
    try:
        logger.info("Запуск сервера Uvicorn")
        uvicorn.run(app, host="127.0.0.1", port=8080)
    except Exception as e:
        logger.exception("Ошибка запуска Uvicorn сервера: %s", e)
