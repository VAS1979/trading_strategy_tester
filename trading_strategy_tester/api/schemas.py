" Содержит модели Pydantic"

from decimal import Decimal

from pydantic import BaseModel


class RequestParameters(BaseModel):
    """
    Модель для входных данных парсера.

    Атрибуты:
        ticker (str): Тикер акции.
        start (str): Начальная дата запроса истории торгов.
        end (str): Конечная дата запроса истории торгов.
    """

    ticker: str
    start: str
    end: str


class StrategyParameters(BaseModel):
    """
    Модель для входных данных торговой стратегии.

    Атрибуты:
        initial_cache (Decimal): Сумма кэша на начало стратегии.
        buy_price (Decimal): Цена покупки акций.
        sell_price (Decimal): Цена продажи акций.
        commission_rate (Decimal): Процентая ставка комиссии брокера.
        tax_rate (Decimal): Налоговая ставка.
    """

    ticker: str
    initial_cache: Decimal
    buy_price: Decimal
    sell_price: Decimal
    commission_rate: Decimal
    tax_rate: Decimal
