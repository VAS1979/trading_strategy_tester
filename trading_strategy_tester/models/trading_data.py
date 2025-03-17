""" Содержит класс для хранения данных о торговом дне """

from dataclasses import dataclass


@dataclass
class TradingData:
    """
    Класс для хранения данных о торговом дне.

    Атрибуты:
        date (str): Дата торгов в формате 'YYYY-MM-DD'.
        high (float): Максимальная цена за день.
        low (float): Минимальная цена за день.
        close (float): Цена закрытия дня.
    """

    date: str
    high: float
    low: float
    close: float
