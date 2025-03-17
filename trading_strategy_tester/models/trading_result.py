""" Содержит класс для хранения результатов торговой
стратегии на конкретную дату. """

from dataclasses import dataclass


@dataclass
class TradingResult:
    """
    Класс для хранения результатов торговой стратегии на конкретную дату.

    Атрибуты:
        date_str (str): Дата торгов в формате 'YYYY-MM-DD'.
        max_price (float): Максимальная цена за день.
        min_price (float): Минимальная цена за день.
        cache (float): Остаток денежных средств на конец дня.
        share_count (int): Количество акций в портфеле на конец дня.
        amount_in_shares (float): Стоимость акций в портфеле на конец дня.
        overall_result (float): Общая стоимость портфеля на конец дня.
        comiss_sum (float): Сумма комиссии, уплаченной за день.
        tax_sum (float): Сумма налога, уплаченного за день.
        total_tax (float): Общая сумма налога, уплаченного за весь период.
    """

    date_str: str
    max_price: float
    min_price: float
    cache: float
    share_count: int
    amount_in_shares: float
    overall_result: float
    comiss_sum: float
    tax_sum: float
    total_tax: float
