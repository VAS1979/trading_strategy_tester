""" Содержит функцию, которая прреобразует DataFrame в
список объектов StockCandle с str значениями. """

from typing import List
import pandas as pd

from trading_strategy_tester.models.stock_candle import StockCandle


def converts_to_str(df: pd.DataFrame) -> List[StockCandle]:
    """
    Преобразует DataFrame в список объектов StockCandle с str значениями.

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
            open=str(row['open']),
            close=str(row['close']),
            high=str(row['high']),
            low=str(row['low']),
            value=str(row['value']),
            volume=str(row['volume']),
            begin=row['begin'],
            end=row['end']
        )
        candles.append(candle)

    return candles
