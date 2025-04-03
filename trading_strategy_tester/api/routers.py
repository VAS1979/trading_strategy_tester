""" Маршруты FastAPI """

from decimal import Decimal
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_strategy_tester.api.schemas import (RequestParameters,
                                                 StrategyParameters)
from trading_strategy_tester.services.facade import Facade
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
    success = Facade.run_parsing(parameters)
    return {"success": success}


@router.post("/api/generate-report")
async def generate_report(
    ticker: str = Form(...),
    initial_cache: str = Form(...),
    buy_price: str = Form(...),
    sell_price: str = Form(...),
    commission_rate: str = Form(...),
    tax_rate: str = Form(...)
):
    """
    Запускает торговую стратегию.
    """

    parameters = StrategyParameters(
        ticker=ticker,
        initial_cache=Decimal(initial_cache),
        buy_price=Decimal(buy_price),
        sell_price=Decimal(sell_price),
        commission_rate=Decimal(commission_rate),
        tax_rate=Decimal(tax_rate)
    )
    success = Facade.run_trading_strategy(parameters)
    return {"success": success}
