""" Маршруты FastAPI """

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_strategy_tester.api.schemas import (RequestParameters,
                                                 StrategyParameters)
from trading_strategy_tester.facade.parsing_facade import run_parsing
from trading_strategy_tester.facade.project_facade import run_trading_strategy
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="trading_strategy_tester/templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Возвращает HTML-страницу для ввода данных.
    """
    return templates.TemplateResponse(name="index.html",
                                      context={"request": request})


@router.post("/api/fetch-data")
async def fetch_data(
    ticker: str = Form(...),
    start: str = Form(...),
    end: str = Form(...)
):
    """
    Получает данные с MOEX и сохраняет их в CSV-файл.
    """

    parameters = RequestParameters(
        ticker=ticker,
        start=start,
        end=end
    )
    filepath = f"database/dataframe_history/{ticker}.csv"
    success = run_parsing(parameters, filepath)
    return {"success": success}


@router.post("/api/generate-report")
async def generate_report(
    ticker: str = Form(...),
    initial_cache: float = Form(...),
    buy_price: float = Form(...),
    sell_price: float = Form(...),
    commission_rate: float = Form(...),
    tax_rate: float = Form(...)
):
    """
    Запускает торговую стратегию.
    """

    parameters = StrategyParameters(
        ticker=ticker,
        initial_cache=initial_cache,
        buy_price=buy_price,
        sell_price=sell_price,
        commission_rate=commission_rate,
        tax_rate=tax_rate
    )
    success = run_trading_strategy(ticker, parameters)
    print(success)
    return {"success": success}
