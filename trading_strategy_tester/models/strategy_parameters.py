""" Содержит класс для хранения входных
параметров торговой стратегии. """

from dataclasses import dataclass


@dataclass
class StrategyParameters:
    """ Класс для хранения входных параметров
    торговой стратегии.

    Атрибуты:
        initial_cache (float): Сумма кэша на начало стратегии.
        buy_price (float): Цена покупки акций.
        sell_price (float): Цена продажи акций.
        commission_rate (float): Процентая ставка комиссии брокера.
        tax_rate (float): Налоговая ставка.
    """

    initial_cache: float
    buy_price: float
    sell_price: float
    commission_rate: float
    tax_rate: float
