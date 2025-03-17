""" Парсит инфу по акции на исторических данных """

from dataclasses import dataclass
from moexalgo import Ticker

from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


@dataclass
class RequestParameters:
    """ Класс для хранения данных по
    запросу парсеру """

    ticker: str
    start: str
    end: str


def parses_dataframe(parameters, directory):
    """ Парсит ценовую историю и сохраняет
    датафрейм в csv файл """

    # Обьект класса Ticker
    ticker = Ticker(parameters.ticker)

    # Свечи по акции за период
    df = ticker.candles(start=parameters.start, end=parameters.end, period='1d')

    # Определяет желаемый порядок столбцов.
    desired_columns = ['open', 'close', 'high', 'low', 'value',
                       'volume', 'begin', 'end']
    # Проверяет, существуют ли все столбцы в DataFrame
    missing_cols = set(desired_columns) - set(df.columns)
    if missing_cols:
        logging.error("Ошибка: Столбцы %s отсутствуют в DataFrame",
                      missing_cols)
    else:
        # Сохраняет в CSV-файл с указанным порядком столбцов:
        df.to_csv(directory, columns=desired_columns, index=False)
        logging.info("Данные успешно сохранены в %s", directory)


request = RequestParameters(
    ticker="MTSS",
    start="2014-01-01",
    end="2024-12-28"
)

DIRECTORY = "database/dataframe_history_test/MTSS.csv"

parses_dataframe(request, DIRECTORY)
