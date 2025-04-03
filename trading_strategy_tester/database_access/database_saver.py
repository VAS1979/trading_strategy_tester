"""Содержит класс, сохраняющий данные в базу данных SQLite."""

import sqlite3
from pathlib import Path
from typing import Dict, Iterator, List
from contextlib import contextmanager

from trading_strategy_tester.models.stock_candle import StockCandle
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class ResultSaver:
    """Класс для сохранения результатов расчетов в базу данных."""

    @staticmethod
    def _get_db_path() -> Path:
        """Возвращает путь к файлу базы данных."""

        path_dir = Path.cwd() / "database"
        path_dir.mkdir(parents=True, exist_ok=True)
        return path_dir / "trading_strategy_tester.db"

    @staticmethod
    @contextmanager
    def _get_connection() -> Iterator[sqlite3.Connection]:
        """Контекстный менеджер для подключения к БД."""

        conn = None
        try:
            conn = sqlite3.connect(ResultSaver._get_db_path())
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            logger.error("Ошибка базы данных: %s", e)
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    @contextmanager
    def _get_cursor(conn: sqlite3.Connection) -> Iterator[sqlite3.Cursor]:
        """Контекстный менеджер для работы с курсором."""

        cursor = None
        try:
            cursor = conn.cursor()
            yield cursor
        except sqlite3.Error as e:
            logger.error("Ошибка курсора: %s", e)
            conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _clear_table(cursor: sqlite3.Cursor, table_name: str) -> None:
        """Очищает таблицу, если она существует."""

        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(
            f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"
        )

    @staticmethod
    def saves_candles(candles: List[StockCandle],
                      ticker: str,
                      clear_existing: bool = True) -> Path:
        """Сохраняет свечи в базу данных."""

        filepath = ResultSaver._get_db_path()
        table_name = f"{ticker.lower()}_dataframe"

        with ResultSaver._get_connection() as conn:
            with ResultSaver._get_cursor(conn) as cursor:
                try:
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        open INTEGER NOT NULL,
                        close INTEGER NOT NULL,
                        high INTEGER NOT NULL,
                        low INTEGER NOT NULL,
                        value INTEGER NOT NULL,
                        volume INTEGER NOT NULL,
                        begin TIMESTAMP NOT NULL,
                        end TIMESTAMP NOT NULL,
                        UNIQUE(begin, end) ON CONFLICT REPLACE
                    )
                    """)

                    if clear_existing:
                        ResultSaver._clear_table(cursor, table_name)

                    insert_query = f"""
                    INSERT INTO {table_name}
                    (open, close, high, low, value, volume, begin, end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    for candle in candles:
                        data = (
                            int(candle.open * 100),
                            int(candle.close * 100),
                            int(candle.high * 100),
                            int(candle.low * 100),
                            int(candle.value * 100),
                            int(candle.volume),
                            candle.begin.to_pydatetime(),
                            candle.end.to_pydatetime()
                        )
                        cursor.execute(insert_query, data)

                    conn.commit()
                    logger.info("Сохранено %s датафреймов в %s",
                                len(candles), table_name)
                except sqlite3.Error as e:
                    logger.error("Ошибка сохранения датафреймов: %s", e)
                    conn.rollback()
                    raise

        return filepath

    @staticmethod
    def saves_results(results: List[TradingResult],
                      ticker: str,
                      clear_existing: bool = True) -> Path:
        """Сохраняет результаты в базу данных."""

        filepath = ResultSaver._get_db_path()
        table_name = f"{ticker.lower()}_results"

        with ResultSaver._get_connection() as conn:
            with ResultSaver._get_cursor(conn) as cursor:
                try:
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_str TEXT NOT NULL UNIQUE ON CONFLICT REPLACE,
                        max_price TEXT NOT NULL,
                        min_price TEXT NOT NULL,
                        cache TEXT NOT NULL,
                        share_count INTEGER NOT NULL,
                        amount_in_shares TEXT NOT NULL,
                        overall_result TEXT NOT NULL,
                        comiss_sum TEXT NOT NULL,
                        tax_sum TEXT NOT NULL,
                        total_tax TEXT NOT NULL
                    )
                    """)

                    if clear_existing:
                        ResultSaver._clear_table(cursor, table_name)

                    insert_query = f"""
                    INSERT INTO {table_name}
                    (date_str, max_price, min_price, cache, share_count,
                     amount_in_shares, overall_result, comiss_sum, tax_sum,
                     total_tax)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    for result in results:
                        data = (
                            result.date_str,
                            str(result.max_price),
                            str(result.min_price),
                            str(result.cache),
                            result.share_count,
                            str(result.amount_in_shares),
                            str(result.overall_result),
                            str(result.comiss_sum),
                            str(result.tax_sum),
                            str(result.total_tax)
                        )
                        cursor.execute(insert_query, data)

                    conn.commit()
                    logger.info("Сохранено %s записей в %s",
                                len(results), table_name)
                except sqlite3.Error as e:
                    logger.error("Ошибка сохранения результатов: %s", e)
                    conn.rollback()
                    raise

        return filepath

    @staticmethod
    def saves_calculations(results: Dict[str, any], ticker: str) -> Path:
        """Сохраняет результаты расчетов в базу данных."""

        filepath = ResultSaver._get_db_path()
        table_name = f"{ticker.lower()}_calculations"

        with ResultSaver._get_connection() as conn:
            with ResultSaver._get_cursor(conn) as cursor:
                try:
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        initial_cache TEXT NOT NULL,
                        buy_price TEXT NOT NULL,
                        sell_price TEXT NOT NULL,
                        buy_count INTEGER NOT NULL,
                        sell_count INTEGER NOT NULL,
                        comission_percent TEXT NOT NULL,
                        tax_percent TEXT NOT NULL,
                        invest_period_days INTEGER NOT NULL,
                        invest_period_years TEXT NOT NULL,
                        total_income_sum TEXT NOT NULL,
                        total_income_perc TEXT NOT NULL,
                        incom_year_sum TEXT NOT NULL,
                        incom_year_pers TEXT NOT NULL,
                        accumulated_commission TEXT NOT NULL,
                        final_cache TEXT NOT NULL,
                        final_amount_in_shares TEXT NOT NULL,
                        final_overall_result TEXT NOT NULL,
                        total_tax TEXT NOT NULL,
                        UNIQUE(start_date, end_date, initial_cache,
                               buy_price, sell_price)
                        ON CONFLICT REPLACE
                    )
                    """)

                    cursor.execute(f"""
                    INSERT INTO {table_name} (
                        start_date, end_date, initial_cache, buy_price,
                        sell_price, buy_count, sell_count, comission_percent,
                        tax_percent, invest_period_days, invest_period_years,
                        total_income_sum, total_income_perc, incom_year_sum,
                        incom_year_pers, accumulated_commission, final_cache,
                        final_amount_in_shares, final_overall_result, total_tax
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        results["start_date"],
                        results["end_date"],
                        str(results.get("initial_cache", "0")),
                        str(results.get("buy_price", "0")),
                        str(results.get("sell_price", "0")),
                        int(results.get("buy_count", 0)),
                        int(results.get("sell_count", 0)),
                        str(results.get("comission_percent", "0")),
                        str(results.get("tax_percent", "0")),
                        int(results.get("invest_period_days", 0)),
                        str(results.get("invest_period_years", "0")),
                        str(results.get("total_income_sum", "0")),
                        str(results.get("total_income_perc", "0")),
                        str(results.get("incom_year_sum", "0")),
                        str(results.get("incom_year_pers", "0")),
                        str(results.get("accumulated_commission", "0")),
                        str(results.get("final_cache", "0")),
                        str(results.get("final_amount_in_shares", "0")),
                        str(results.get("final_overall_result", "0")),
                        str(results.get("total_tax", "0"))
                    ))

                    conn.commit()
                    logger.info("Сохранение расчетов в %s", table_name)
                except sqlite3.Error as e:
                    logger.error("Ошибка сохранения расчетов: %s", e)
                    conn.rollback()
                    raise

        return filepath
