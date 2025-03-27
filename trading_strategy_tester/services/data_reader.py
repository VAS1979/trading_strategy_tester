""" Содержит класс для чтения данных из CSV-файла,
сформированного парсером. """

from pathlib import Path
import csv
from typing import List, Optional
from trading_strategy_tester.models.trading_data import TradingData
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class DataReader:
    """
    Класс для чтения данных из CSV-файла,
    сформированного парсером.
    """

    def __init__(self, ticker: str):
        """
        Инициализация класса DataReader.

        Args:
            ticker (str): Наименование тикера акции.
        """
        path_dir = Path.cwd() / "database" / "dataframe_history"
        csv_file = f"{ticker}.csv"
        filepath = path_dir / csv_file
        self.filepath = filepath

    def read_csv_with_header(self) -> Optional[List[TradingData]]:
        """
        Считывает CSV-файл с историческими данными и возвращает
        список объектов TradingData. Считываемый csv файл имеет колонки:
            (open, close, high, low, value, volume, begin, end).

        Variables:
        data_list: Список для сохраняемых.
        closing_price: Цена закрытия дня.
        high_value: Максимальная цена за день.
        low_value: Минимальная цена за день.

        Returns:
            Optional[List[TradingData]]: Список объектов TradingData,
            каждый из которых описывает состояние
            торгового портфеля на определённую дату: [дата (str),
            максимальная цена (float), минимальная цена (float), цена закрытия
            дня (float)]. В случае ошибки возвращает None.
        """

        try:
            data_list = []
            with open(self.filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        closing_price = float(row['close'].replace(',', '.'))
                        high_value = float(row['high'].replace(',', '.'))
                        low_value = float(row['low'].replace(',', '.'))
                        data_list.append(TradingData(row['begin'], high_value,
                                                     low_value, closing_price))
                    except ValueError as e:
                        logger.error("Ошибка преобразования значения в число "
                                     "в строке %s, ошибка: %s", row, e)
                        raise
                    except KeyError as e:
                        logger.error("Столбец %s не найден в "
                                     "строке: %s", e, row)
                        raise
            logger.info("Считывание CSV-файла, "
                        "сохранение списка объектов TradingData...")
            return data_list
        except FileNotFoundError as e:
            logger.error("Файл %s не найден, ошибка: %s", self.filepath, e)
            return None
        except Exception as e:
            logger.error("Произошла общая ошибка: %s", e)
            return None
