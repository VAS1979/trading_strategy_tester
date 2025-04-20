""" Содержит методы класса, обрабатывающие цепочку последовательных
вызовов функций и классов для работы приложения. """

from typing import Any

from trading_strategy_tester.api.schemas import RequestParameters, StrategyParameters
from trading_strategy_tester.services.calculate_results import CalculateResult
from trading_strategy_tester.services.convert_df_to_str import converts_to_str
from trading_strategy_tester.services.data_parser import DataframeParser
from trading_strategy_tester.services.database_gateway import DatabaseGateway
from trading_strategy_tester.services.strategy_calculator import StrategyCalculator
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class Facade:
    """Класс обрабатывает цепочку вызовов
    при работе приложения."""

    @staticmethod
    def run_parsing(param: RequestParameters) -> str:
        """Запускает парсер и сохраняет результат в базу данных.

        Args:
            param (RequestParameters): Параметры запроса.
        """
        ticker = param.ticker.upper()

        # Запрос датафрэйма
        parser = DataframeParser(param)
        df = parser.fetch_data()

        # Преобразование DataFrame в список объектов StockCandle с str.
        processed_df = converts_to_str(df)

        # Сохранение данных парсера в SQL
        gateway = DatabaseGateway()
        gateway.saves_candles(processed_df, ticker)

        result = f"Исторические данные {ticker} успешно загружены."
        return result

    @staticmethod
    def run_trading_strategy(param: StrategyParameters) -> dict[str, Any]:
        """
        Запускает торговую стратегию и возвращает результаты.

        Args:
            param (StrategyParameters): Параметры стратегии.

        Returns:
            Optional[Tuple[List[TradingResult], List[int]]]: Результаты
                расчетов и количество сделок.
        """

        ticker = param.ticker.upper()
        gateway = DatabaseGateway()

        # Загрузка истории из базы данных
        sql_data = gateway.load_dataframe_history(ticker)

        # Инициализация StrategyCalculator
        strategy_calculator = StrategyCalculator(param)

        # Расчет данных
        results, transactions = strategy_calculator.calculates_data(sql_data)

        # Рассчет итогов
        calc_result = CalculateResult()
        final_result = calc_result.calculates_results(results, param, transactions)

        # Сохранение результатов стратегии по дням в sql
        gateway.saves_results(results, ticker)

        # Сохранение итоговых рассчетов
        gateway.saves_calculations(final_result, ticker)

        return final_result
