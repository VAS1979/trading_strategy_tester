""" Содержит класс, который парсит датафрейм по акции на
исторических данных. """

from moexalgo import Ticker
import pandas as pd

from trading_strategy_tester.utils.logger import logging
from trading_strategy_tester.api.schemas import RequestParameters

logger = logging.getLogger(__name__)


class DataframeParser:
    """ Класс для обработки запроса и получения
    датафрейм от MOEX. """

    def __init__(self, parameters: RequestParameters):
        """ Инициализация класса DataParser.
        Args:
            parameters (RequestParameters): Параметры запроса.
        """

        self.parameters = parameters

    def fetch_data(self) -> pd.DataFrame:
        """
        Получает данные по акции за указанный период.

        Returns:
            pd.DataFrame: DataFrame с данными по акции.
        """

        try:
            # Объект класса Ticker
            ticker = Ticker(self.parameters.ticker)

            # Свечи по акции за период
            df = ticker.candles(start=self.parameters.start,
                                end=self.parameters.end, period='1d')

            # Проверка, что данные получены
            if df.empty:
                logger.warning("Нет данных за указанный период.")
                return pd.DataFrame()
            logger.info("Запрошенный датафрейм получен.")
            return df

        except Exception as e:
            logger.error("Ошибка при получении данных: %s", e)
            raise
