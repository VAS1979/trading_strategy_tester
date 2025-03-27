""" Содержит класс для сохранения результатов вычислений стратегии. """

from pathlib import Path
import csv
import json
from typing import Dict, List
import pandas as pd

from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class ResultSaver:
    """
    Класс для сохранения результатов в CSV.
    """

    def saves_result_to_csv(self, data: List[TradingResult],
                            columns: List[str], ticker: str) -> None:
        """
        Сохраняет результаты в CSV-файл.

        Args:
            data (List[TradingResult]): Данные для сохранения.
            columns (List[str]): Заголовки столбцов.
            ticker (str): Наименование тикера акции.
        """

        if data is None:
            logger.error("Нет данных для сохранения.")
            return

        path_dir = Path.cwd() / "database" / "processed_data_csv"
        csv_file = f"{ticker}.csv"
        filepath = path_dir / csv_file
        try:
            with open(filepath, 'w', newline='', encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows([list(row.__dict__.values()) for row in data])
                logger.info("Сохранение итоговых результатов в "
                            "файл %s", filepath)
        except IOError as e:
            logger.error("Ошибка записи в файл %s: %s", csv_file, e)
            raise
        except Exception as e:
            logger.exception("Непредвиденная ошибка при"
                             "сохранении в файл %s: %s", csv_file, e)
            raise

    def saves_result_to_json(self, results: Dict[str, any],
                             ticker: str) -> None:
        """
        Сохраняет результаты в JSON-файл.

        Args:
            results (Dict[str, any]): Словарь с результатами.
            ticker (str): Наименование тикера акции.
        """

        path_dir = Path.cwd() / "database" / "processed_data_json"
        json_file = f"{ticker}.json"
        filepath = path_dir / json_file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logger.info("Результаты успешно сохранены в файл %s.", json_file)
        except IOError as e:
            logger.exception("Ошибка при записи в файл: %s", e)
            raise

    def saves_dataframe_to_csv(self, df: pd.DataFrame, ticker: str) -> None:
        """
        Сохраняет DataFrame в CSV-файл.

        Args:
            df (pd.DataFrame): DataFrame с данными.
            columns (List[str]): Заголовки столбцов.
            ticker (str):  Наименование акции.
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
                path_dir = Path.cwd() / "database" / "dataframe_history"
                csv_file = f"{ticker}.csv"
                filepath = path_dir / csv_file
                df.to_csv(filepath, columns=desired_columns, index=False)
                logging.info("Данные успешно сохранены в %s", filepath)

        except IOError as e:
            logger.error("Ошибка записи в файл %s: %s", csv_file, e)
            raise
        except Exception as e:
            logger.exception("Непредвиденная ошибка при сохранении в "
                             "файл %s: %s", csv_file, e)
            raise
