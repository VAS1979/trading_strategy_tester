""" Содержит функцию, обрабатывающую цепочку последовательных
вызовов функций и классов для работы стратегии. """

from typing import Optional, Tuple, List
from trading_strategy_tester.services.data_reader import DataReader
from trading_strategy_tester.services.strategy_calculator import (
    StrategyCalculator)
from trading_strategy_tester.services.calculate_results import CalculateResult
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.services.result_saver import ResultSaver
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


def run_trading_strategy(
    ticker: str,
    param: StrategyParameters
) -> Optional[Tuple[List[TradingResult], List[int]]]:
    """
    Запускает торговую стратегию и возвращает результаты.

    Args:
        ticker (str): Тикер акции.
        param (StrategyParameters): Параметры стратегии.

    Returns:
        Optional[Tuple[List[TradingResult], List[int]]]: Результаты расчетов
        и количество сделок.
    """

    # Наименование колонок итогового CSV отчета
    columns = ['date', 'high', 'low', 'cache', 'share_count',
               'amount_in_shares', 'overall_result', 'comission',
               'tax', 'total_tax']

    # Путь к папке данными.
    output_path = "database"

    # Инициализация DataReader
    filepath = f"database/dataframe_history/{ticker}.csv"
    data_reader = DataReader(filepath=filepath)

    # Чтение данных
    data = data_reader.read_csv_with_header()
    if data is None:
        raise ValueError("Не удалось загрузить данные из CSV.")

    # Инициализация StrategyCalculator
    strategy_calculator = StrategyCalculator(param)

    # Расчет данных
    results, transactions = strategy_calculator.calculates_data(data)

    save_result = ResultSaver()
    if not results:
        logger.warning("Нет данных для сохранения.")
    else:
        save_result.saves_result_to_csv(results, columns, output_path, ticker)

    calc_result = CalculateResult()
    final_result = calc_result.calculates_results(results, param, transactions)

    save_result.saves_result_to_json(final_result, output_path, ticker)

    return final_result
