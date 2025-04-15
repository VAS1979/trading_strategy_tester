""" Модуль для хранения данных о торговых свечах с
строковым представлением дат """

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
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
    end: str    # Строка даты в ISO формате

    @classmethod
    def from_pd_timestamp(cls,
                          open: Decimal,
                          close: Decimal,
                          high: Decimal,
                          low: Decimal,
                          value: Decimal,
                          volume: Decimal,
                          begin: pd.Timestamp,
                          end: pd.Timestamp):
        """Альтернативный конструктор для создания из pandas.Timestamp.

        Args:
            open: Цена открытия
            close: Цена закрытия
            high: Максимальная цена
            low: Минимальная цена
            value: Оборот в рублях
            volume: Объем в штуках
            begin: Время начала (pd.Timestamp)
            end: Время окончания (pd.Timestamp)
            
        Returns:
            StockCandle: Созданный объект свечи
        """
        return cls(
            open=open,
            close=close,
            high=high,
            low=low,
            value=value,
            volume=volume,
            begin=begin.isoformat(sep=' ', timespec='seconds'),
            end=end.isoformat(sep=' ', timespec='seconds')
        )

    @classmethod
    def from_datetime(cls,
                      open: Decimal,
                      close: Decimal,
                      high: Decimal,
                      low: Decimal,
                      value: Decimal,
                      volume: Decimal,
                      begin: datetime,
                      end: datetime):
        """Альтернативный конструктор для создания из datetime.

        Args:
            begin: Время начала (datetime)
            end: Время окончания (datetime)
        """
        return cls(
            open=open,
            close=close,
            high=high,
            low=low,
            value=value,
            volume=volume,
            begin=begin.isoformat(sep=' ', timespec='seconds'),
            end=end.isoformat(sep=' ', timespec='seconds')
        )
