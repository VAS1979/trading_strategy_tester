" . "

from pydantic import BaseModel


class StrategyInput(BaseModel):
    """
    Модель для входных данных торговой стратегии.
    """
    initial_cache: float
    buy_price: float
    close_price: float
    commission: float
    tax: float
    tax_strategy: str = "yearly"


class StrategyOutput(BaseModel):
    """
    Модель для выходных данных торговой стратегии.
    """
    transactions: list
    final_result: dict
