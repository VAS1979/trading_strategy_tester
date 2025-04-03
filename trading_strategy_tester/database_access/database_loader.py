"""Содержит класс, для загрузки из SQLite базы данных."""

import sqlite3
from pathlib import Path
from decimal import Decimal
from typing import List, Optional, Iterator
from contextlib import contextmanager
import pandas as pd

from trading_strategy_tester.models.stock_candle import StockCandle


class DatabaseLoader:
    """Класс для загрузки данных свечей из базы данных."""

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
            conn = sqlite3.connect(DatabaseLoader._get_db_path())
            yield conn
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Ошибка подключения к базе данных: {e}")
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
            conn.rollback()
            raise sqlite3.Error(f"Ошибка курсора: {e}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
        """Проверяет существование таблицы в базе данных."""

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    @staticmethod
    def load_history_from_db(ticker: str) -> List[StockCandle]:
        """
        Загружает данные свечей из SQLite базы данных.

        Args:
            ticker: Тикер акции.

        Returns:
            List[StockCandle]: Список объектов свечей.

        Raises:
            ValueError: Если таблица не существует.
            sqlite3.Error: При ошибках работы с БД.
        """

        table_name = f"{ticker.lower()}_dataframe"

        try:
            with DatabaseLoader._get_connection() as conn:
                with DatabaseLoader._get_cursor(conn) as cursor:
                    if not DatabaseLoader._table_exists(cursor, table_name):
                        raise ValueError(
                            f"Таблица {table_name} не найдена в базе данных"
                        )

                    cursor.execute(f"""
                        SELECT open, close, high, low, value, volume,
                        begin, end
                        FROM {table_name}
                        ORDER BY begin
                        """)

                    return [
                        StockCandle(
                            open=Decimal(row[0]) / 100,
                            close=Decimal(row[1]) / 100,
                            high=Decimal(row[2]) / 100,
                            low=Decimal(row[3]) / 100,
                            value=Decimal(row[4]) / 100,
                            volume=Decimal(row[5]),
                            begin=str(row[6]),
                            end=str(row[7])
                        )
                        for row in cursor
                    ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Ошибка при загрузке данных: {e}")

    @staticmethod
    def get_last_date(ticker: str) -> Optional[pd.Timestamp]:
        """
        Возвращает дату последней свечи в базе.

        Args:
            ticker: Тикер акции

        Returns:
            Optional[pd.Timestamp]: Метка времени последней свечи или None.

        Raises:
            FileNotFoundError: Если база данных не существует
            sqlite3.Error: При ошибках работы с БД
        """

        filepath = DatabaseLoader._get_db_path()
        table_name = f"{ticker.lower()}_dataframe"

        if not filepath.exists():
            raise FileNotFoundError(f"Файл базы данных {filepath} не найден")

        try:
            with DatabaseLoader._get_connection() as conn:
                with DatabaseLoader._get_cursor(conn) as cursor:
                    if not DatabaseLoader._table_exists(cursor, table_name):
                        return None

                    cursor.execute(f"""
                        SELECT end FROM {table_name}
                        ORDER BY end DESC
                        LIMIT 1
                        """)

                    result = cursor.fetchone()
                    return pd.Timestamp(result[0]) if result else None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Ошибка при получении даты: {e}")
