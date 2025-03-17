""" Содержит функцию, обрабатывающую цепочку последовательных
вызовов функций и классов для работы парсера. """

from trading_strategy_tester.services.result_saver import ResultSaver
from trading_strategy_tester.utils.logger import logging
from trading_strategy_tester.services.data_parser import DataframeParser
from trading_strategy_tester.models.request_parameters import (
    RequestParameters)

logger = logging.getLogger(__name__)


def run_parsing(param: RequestParameters, filepath: str) -> None:
    """ Запускает парсер и сохраняет результат в CSV файл.

    Args:
        param (RequestParameters): Параметры запроса.
        filepath (str): Путь сохранения CSV-файла.
    """

    # Запрос датафрэйма
    request = DataframeParser(param)
    data = request.fetch_data()

    # Сохранение в файл
    saver = ResultSaver()
    saver.saves_dataframe_to_csv(data, filepath)


parameters = RequestParameters(
    ticker="MTSS",
    start="2014-01-01",
    end="2024-12-28"
)

DIRECTORY = "database/dataframe_history/MTSS.csv"

run_parsing(parameters, DIRECTORY)
