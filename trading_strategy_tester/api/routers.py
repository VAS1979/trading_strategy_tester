""" Маршруты FastAPI """

from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_strategy_tester.api.schemas import RequestParameters, StrategyParameters
from trading_strategy_tester.services.database_gateway import DatabaseGateway
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
    return templates.TemplateResponse(name="index.html", context={"request": request})


@router.post("/api/fetch-data")
async def fetch_data(params: Annotated[RequestParameters, Form()]):
    """
    Получает данные с MOEX и сохраняет их в CSV-файл.
    """

    success = Facade.run_parsing(param=params)
    return {"success": success}


@router.post("/api/generate-report")
async def generate_report(params: Annotated[StrategyParameters, Form()]):
    """
    Запускает торговую стратегию.
    """
    success = Facade.run_trading_strategy(param=params)
    return {"success": success}


@router.post("/api/show-history")
async def show_history(ticker: Annotated[str, Form()]):
    """
    Возвращает HTML таблицу с историей торговой стратегии.
    Данные берутся из таблицы {ticker}_results в БД.
    """

    gateway = DatabaseGateway()
    results = gateway.load_strategy_results(ticker)

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

    return {"success": True, "html_table": html_table, "ticker": ticker.upper()}
