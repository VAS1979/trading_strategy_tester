" . "

from pydantic import BaseModel


class RequestParameters(BaseModel):
    """
    Модель для входных данных парсера.

    Атрибуты:
        ticker (str): Тикер акции.
        start (str): Начальная дата запроса истории торгов.
        end (str): Конечеая дата запроса истории торгов.
    """

    ticker: str
    start: str
    end: str


class StrategyParameters(BaseModel):
    """
    Модель для входных данных торговой стратегии.

    Атрибуты:
        initial_cache (float): Сумма кэша на начало стратегии.
        buy_price (float): Цена покупки акций.
        sell_price (float): Цена продажи акций.
        commission_rate (float): Процентая ставка комиссии брокера.
        tax_rate (float): Налоговая ставка.
    """

    ticker: str
    initial_cache: float
    buy_price: float
    sell_price: float
    commission_rate: float
    tax_rate: float
