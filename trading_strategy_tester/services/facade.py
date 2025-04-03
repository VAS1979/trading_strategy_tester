""" Содержит методы класса, обрабатывающие цепочку последовательных
вызовов функций и классов для работы приложения. """

from typing import Optional, Tuple, List

from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.api.schemas import RequestParameters
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.services.data_parser import DataframeParser
from trading_strategy_tester.services.convert_to_decimal import (
    converts_to_decimal)
from trading_strategy_tester.services.strategy_calculator import (
    StrategyCalculator)
from trading_strategy_tester.services.calculate_results import CalculateResult
from trading_strategy_tester.database_access.database_saver import (
    ResultSaver)
from trading_strategy_tester.database_access.database_loader import (
    DatabaseLoader)
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class Facade:
    """ Класс обрабатывает цепочку вызовов
    при работе приложения. """

    @staticmethod
    def run_parsing(param: RequestParameters) -> str:
        """ Запускает парсер и сохраняет результат в базу данных.

        Args:
            param (RequestParameters): Параметры запроса.
        """

        ticker = param.ticker.upper()

        # Запрос датафрэйма
        parser = DataframeParser(param)
        df = parser.fetch_data()

        # Преобразование DataFrame в список объектов StockCandle с Decimal.
        processed_df = converts_to_decimal(df)

        # Сохранение данных парсера в SQL
        ResultSaver.saves_candles(processed_df, ticker)

        result = f"Исторические данные {ticker} успешно загружены."
        return result

    @staticmethod
    def run_trading_strategy(
        param: StrategyParameters
         ) -> Optional[Tuple[List[TradingResult], List[int]]]:
        """
        Запускает торговую стратегию и возвращает результаты.

        Args:
            param (StrategyParameters): Параметры стратегии.

        Returns:
            Optional[Tuple[List[TradingResult], List[int]]]: Результаты
                расчетов и количество сделок.
        """

        ticker = param.ticker.upper()

        # Загрузка истории из базы данных
        sql_data = DatabaseLoader.load_history_from_db(ticker)

        # Инициализация StrategyCalculator
        strategy_calculator = StrategyCalculator(param)

        # Расчет данных
        results, transactions = strategy_calculator.calculates_data(sql_data)

        # Рассчет итогов
        calc_result = CalculateResult()
        final_result = calc_result.calculates_results(results, param,
                                                      transactions)

        # Сохранение результатов стратегии по дням в sql
        ResultSaver.saves_results(results, ticker)

        # Сохранение итоговых рассчетов
        ResultSaver.saves_calculations(final_result, ticker)

        return final_result
