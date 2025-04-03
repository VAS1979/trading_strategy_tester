""" Содержит класс для хранения результатов торговой
стратегии на конкретную дату. """

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TradingResult:
    """
    Класс для хранения результатов торговой стратегии на конкретную дату.

    Атрибуты:
        date_str (str): Дата торгов в формате 'YYYY-MM-DD'.
        max_price (Decimal): Максимальная цена за день.
        min_price (Decimal): Минимальная цена за день.
        cache (Decimal): Остаток денежных средств на конец дня.
        share_count (int): Количество акций в портфеле на конец дня.
        amount_in_shares (Decimal): Стоимость акций в портфеле на конец дня.
        overall_result (Decimal): Общая стоимость портфеля на конец дня.
        comiss_sum (Decimal): Сумма комиссии, уплаченной за день.
        tax_sum (Decimal): Сумма налога, уплаченного за день.
        total_tax (Decimal): Общая сумма налога, уплаченного за весь период.
    """

    date_str: str
    max_price: Decimal
    min_price: Decimal
    cache: Decimal
    share_count: int
    amount_in_shares: Decimal
    overall_result: Decimal
    comiss_sum: Decimal
    tax_sum: Decimal
    total_tax: Decimal
