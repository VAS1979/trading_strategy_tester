from decimal import Decimal
from typing import List

import pandas as pd

from trading_strategy_tester.models.stock_candle import StockCandle


def converts_to_decimal(df: pd.DataFrame) -> List[StockCandle]:
    """
    Преобразует DataFrame в список объектов StockCandle с Decimal значениями.

    Args:
        df (pd.DataFrame): Исходный DataFrame с данными свечей.

    Returns:
        List[StockCandle]: Список объектов StockCandle.
    """

    if df.empty:
        return []

    candles = []
    for _, row in df.iterrows():
        candle = StockCandle(
            open=Decimal(str(row["open"])),
            close=Decimal(str(row["close"])),
            high=Decimal(str(row["high"])),
            low=Decimal(str(row["low"])),
            value=Decimal(str(row["value"])),
            volume=Decimal(str(row["volume"])),
            begin=row["begin"],
            end=row["end"],
        )
        candles.append(candle)

    return candles
