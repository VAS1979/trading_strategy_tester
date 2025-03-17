""" Содержит функцию, обрабатывающую цепочку последовательных
вызовов функций и классов для работы стратегии. """

from typing import Optional, Tuple, List
from trading_strategy_tester.services.data_reader import DataReader
from trading_strategy_tester.services.strategy_calculator import (
    StrategyCalculator)
from trading_strategy_tester.services.calculate_results import CalculateResult
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.models.strategy_parameters import (
    StrategyParameters)
from trading_strategy_tester.services.result_saver import ResultSaver
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


def run_trading_strategy(
    filepath: str,
    param: StrategyParameters,
    columns,
    output_path,
) -> Optional[Tuple[List[TradingResult], List[int]]]:
    """
    Запускает торговую стратегию и возвращает результаты.

    Args:
        filepath (str): Путь к CSV-файлу с историческими данными.
        param (StrategyParameters): Параметры стратегии.
        columns: (List[str]): Заголовки столбцов.
        output_path (str): Путь для сохранения файла с результатами.

    Returns:
        Optional[Tuple[List[TradingResult], List[int]]]: Результаты расчетов
        и количество сделок.
    """

    # Инициализация DataReader
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
        save_result.saves_result_to_csv(results, columns, output_path)

    calc_result = CalculateResult()
    final_result = calc_result.calculates_results(results, param, transactions)

    save_result.saves_result_to_json(final_result, output_path)

    return results, transactions


# Наименование колонок итогового CSV отчета
COLUMNS = ['date', 'high', 'low', 'cache', 'share_count', 'amount_in_shares',
           'overall_result', 'comission', 'tax', 'total_tax']
# Путь к сформированному отчету
FILEPATH_TO_FINISH_DATA = "database/processed_data/MTSS"

parameters = StrategyParameters(
        initial_cache=400000,
        buy_price=215.0,
        sell_price=300.0,
        commission_rate=0.00035,
        tax_rate=0.13
    )

readed_datframe = run_trading_strategy("database/dataframe_history/MTSS.csv",
                                       parameters, COLUMNS,
                                       FILEPATH_TO_FINISH_DATA)
