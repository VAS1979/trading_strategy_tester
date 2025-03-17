""" Содержит класс для сохранения результатов вычислений. """

import csv
import json
import pandas as pd
from typing import Dict, List

from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class ResultSaver:
    """
    Класс для сохранения результатов в CSV.
    """

    def saves_result_to_csv(self, data: List[TradingResult],
                            columns: List[str], filename: str) -> None:
        """
        Сохраняет результаты в CSV-файл.

        Args:
            data (List[TradingResult]): Данные для сохранения.
            columns (List[str]): Заголовки столбцов.
            filename (str): Путь к файлу.
        """

        if data is None:
            logger.error("Нет данных для сохранения.")
            return

        try:
            filename = filename + ".csv"
            with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows([list(row.__dict__.values()) for row in data])
                logger.info("Сохранение итоговых результатов в "
                            "файл %s", filename)
        except IOError as e:
            logger.error("Ошибка записи в файл %s: %s", filename, e)
            raise
        except Exception as e:
            logger.exception("Непредвиденная ошибка при"
                             "сохранении в файл %s: %s", filename, e)
            raise

    def saves_result_to_json(self, results: Dict[str, any],
                             filename: str) -> None:
        """
        Сохраняет результаты в JSON-файл.

        Args:
            results (Dict[str, any]): Словарь с результатами.
            filename (str): Имя файла для сохранения (без расширения).
        """
        try:
            filename = filename + ".json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logger.info("Результаты успешно сохранены в файл %s.", filename)
        except IOError as e:
            logger.exception("Ошибка при записи в файл: %s", e)
            raise

    def saves_dataframe_to_csv(self, df: pd.DataFrame, directory: str) -> None:
        """
        Сохраняет DataFrame в CSV-файл.

        Args:
            df (pd.DataFrame): DataFrame с данными.
            columns (List[str]): Заголовки столбцов.
            filename (str): Путь к файлу.
        """
        if df is None or df.empty:
            logger.error("Нет данных для сохранения.")
            return

        try:
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

        except IOError as e:
            logger.error("Ошибка записи в файл %s: %s", directory, e)
            raise
        except Exception as e:
            logger.exception("Непредвиденная ошибка при сохранении в "
                             "файл %s: %s", directory, e)
            raise
