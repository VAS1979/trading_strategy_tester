""" Содержит методы класса, обрабатывающие цепочку последовательных
вызовов функций и классов для работы приложения. """

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, List

from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.api.schemas import RequestParameters
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.services.data_parser import DataframeParser
from trading_strategy_tester.services.convert_df_to_str import (
    converts_to_str)
from trading_strategy_tester.services.database_gateway import DatabaseGateway
from trading_strategy_tester.services.strategy_calculator import (
    StrategyCalculator)
from trading_strategy_tester.services.calculate_results import CalculateResult

logger = logging.getLogger(__name__)


class Facade:
    """ Класс обрабатывает цепочку вызовов
    при работе приложения. """

    # Пул потоков для синхронных операций
    _thread_pool = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    async def run_parsing(param: RequestParameters) -> str:
        """ Запускает парсер и сохраняет результат в базу данных.

        Args:
            param (RequestParameters): Параметры запроса.
        """

        ticker = param.ticker.upper()

        # Запрос датафрэйма
        parser = DataframeParser(param)
        df = parser.fetch_data()

        # Преобразование DataFrame в список объектов StockCandle с str.
        processed_df = converts_to_str(df)

        # Функция для сохранения в БД
        async def save_to_db():
            async with DatabaseGateway() as gateway:
                await gateway.saves_candles(processed_df, ticker)

        # Сохранение в БД
        await save_to_db()

        result = f"Исторические данные {ticker} успешно загружены."
        return result

    @staticmethod
    async def run_trading_strategy(
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

        # Асинхронная загрузка данных из БД
        async with DatabaseGateway() as gateway:
            sql_data = await gateway.load_dataframe_history(ticker)

        # Инициализация StrategyCalculator
        strategy_calculator = StrategyCalculator(param)

        # Расчет данных
        results, transactions = strategy_calculator.calculates_data(sql_data)

        # Рассчет итогов
        calc_result = CalculateResult()
        final_result = calc_result.calculates_results(results, param,
                                                      transactions)

        # Асинхронное сохранение результатов
        async with DatabaseGateway() as gateway:
            await gateway.saves_results(results, ticker)

        async with DatabaseGateway() as gateway:
            await gateway.saves_calculations(final_result, ticker)

        return final_result
