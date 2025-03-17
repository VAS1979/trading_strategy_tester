""" Маршруты FastAPI """

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_strategy_tester.facade.project_facade import run_trading_strategy
from trading_strategy_tester.api.schemas import StrategyInput, StrategyOutput

router = APIRouter()
templates = Jinja2Templates(directory="trading_strategy_tester/templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Возвращает HTML-страницу для ввода данных.
    """
    return templates.TemplateResponse(name="index.html",
                                      context={"request": request})


@router.post("/generate-report", response_model=StrategyOutput)
async def generate_report(
    initial_cache: float = Form(...),
    buy_price: float = Form(...),
    close_price: float = Form(...),
    commission: float = Form(...),
    tax: float = Form(...),
    tax_strategy: str = Form("yearly")
):
    """
    Обрабатывает данные, введенные пользователем, и возвращает результаты.
    """
    # Запуск торговой стратегии
    results, transactions = run_trading_strategy(
        filepath="dataframe_history/MTSS.csv",
        initial_cache=initial_cache,
        buy_price=buy_price,
        close_price=close_price,
        commission=commission,
        tax=tax,
        tax_strategy=tax_strategy,
        output_csv_path="processed_data/MTSS.csv",
        output_json_path="processed_data/MTSS.json"
    )

    # Возвращаем результаты
    return {
        "transactions": transactions,
        "final_result": results[-1].__dict__
    }
