""" Модуль для хранения данных о торговых свечах с
строковым представлением дат """

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import pandas as pd


@dataclass
class StockCandle:
    """Датакласс для хранения данных свечи акции.

    Хранит:
    - Цены как Decimal для точных расчетов
    - Даты в строковом ISO формате (YYYY-MM-DD HH:MM:SS)
    """

    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    value: Decimal
    volume: Decimal
    begin: str  # Строка даты в ISO формате
    end: str  # Строка даты в ISO формате

    def __init__(
        self,
        open: str | Decimal,
        close: str | Decimal,
        high: str | Decimal,
        low: str | Decimal,
        value: str | Decimal,
        volume: str | Decimal,
        begin: pd.Timestamp | datetime | str,
        end: pd.Timestamp | datetime | str,
    ):
        """Преобразует поля в Decimal"""
        self.open = Decimal(open)
        self.close = Decimal(close)
        self.high = Decimal(high)
        self.low = Decimal(low)
        self.value = Decimal(value)
        self.volume = Decimal(volume)

        if isinstance(begin, pd.Timestamp):
            begin = begin.to_pydatetime()

        if isinstance(end, pd.Timestamp):
            end = end.to_pydatetime()

        if isinstance(begin, str):
            self.begin = begin
        else:
            self.begin = begin.isoformat(sep=" ", timespec="seconds")

        if isinstance(end, str):
            self.end = end
        else:
            self.end = end.isoformat(sep=" ", timespec="seconds")
