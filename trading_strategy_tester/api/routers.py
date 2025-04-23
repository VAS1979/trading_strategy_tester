"""Маршруты FastAPI."""

import logging
from decimal import Decimal
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_strategy_tester.api.schemas import (RequestParameters,
                                                 StrategyParameters)
from trading_strategy_tester.services.facade import Facade
from trading_strategy_tester.services.database_gateway import DatabaseGateway

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
    """Получает данные с MOEX и сохраняет их."""
    parameters = RequestParameters(
        ticker=ticker,
        start=start,
        end=end
    )
    success = await Facade.run_parsing(parameters)
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
    """Запускает торговую стратегию."""
    parameters = StrategyParameters(
        ticker=ticker,
        initial_cache=Decimal(initial_cache),
        buy_price=Decimal(buy_price),
        sell_price=Decimal(sell_price),
        commission_rate=Decimal(commission_rate),
        tax_rate=Decimal(tax_rate)
    )
    success = await Facade.run_trading_strategy(parameters)
    return {"success": success}


@router.post("/api/show-history")
async def show_history(ticker: str = Form(...)):
    """
    Возвращает HTML таблицу с историей торговой стратегии.
    Данные берутся из таблицы {ticker}_results в БД.
    """
    async with DatabaseGateway() as gateway:
        results = await gateway.load_strategy_results(ticker)

    if not results:
        return {"success": False, "error": "Нет данных для отображения"}

    # Формируем HTML таблицу
    html_table = """
    <table class="trading-results">
        <thead>
            <tr>
                <th>Дата</th>
                <th>Максимальная цена</th>
                <th>Минимальная цена</th>
                <th>Кэш</th>
                <th>Количество акций</th>
                <th>Стоимость акций</th>
                <th>Общий результат</th>
                <th>Комиссия</th>
                <th>Налог</th>
                <th>Налог общий</th>
            </tr>
        </thead>
        <tbody>
    """

    for result in results:
        html_table += f"""
        <tr>
            <td>{result['date_str']}</td>
            <td class="numeric">{result['max_price']}</td>
            <td class="numeric">{result['min_price']}</td>
            <td class="numeric">{result['cache']}</td>
            <td class="numeric">{result['share_count']}</td>
            <td class="numeric">{result['amount_in_shares']}</td>
            <td class="numeric">{result['overall_result']}</td>
            <td class="numeric">{result['comiss_sum']}</td>
            <td class="numeric">{result['tax_sum']}</td>
            <td class="numeric">{result['total_tax']}</td>
        </tr>
        """

    html_table += """
        </tbody>
    </table>
    """

    return {
        "success": True,
        "html_table": html_table,
        "ticker": ticker.upper()
    }
