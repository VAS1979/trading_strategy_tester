""" Содержит функцию, обрабатывающую цепочку последовательных
вызовов функций и классов для работы парсера. """

from trading_strategy_tester.services.result_saver import ResultSaver
from trading_strategy_tester.utils.logger import logging
from trading_strategy_tester.services.data_parser import DataframeParser
from trading_strategy_tester.api.schemas import RequestParameters

logger = logging.getLogger(__name__)


def run_parsing(param: RequestParameters, ticker: str) -> None:
    """ Запускает парсер и сохраняет результат в CSV файл.

    Args:
        param (RequestParameters): Параметры запроса.
        ticker (str): Наименование акции.
    """

    # Запрос датафрэйма
    request = DataframeParser(param)
    data = request.fetch_data()

    # Сохранение в файл
    saver = ResultSaver()
    saver.saves_dataframe_to_csv(data, ticker)

    result = f"Исторические данные {param.ticker} успешно загружены."
    return result
