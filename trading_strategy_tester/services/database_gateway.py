"""Модуль для работы с SQLite базой данных тестера торговых стратегий."""

import logging
from pathlib import Path
from decimal import Decimal
from typing import List, Dict
import aiosqlite

from trading_strategy_tester.models.stock_candle import StockCandle
from trading_strategy_tester.models.trading_result import TradingResult

logger = logging.getLogger(__name__)


class DatabaseGateway:
    """Класс для работы с SQLite базой данных тестера торговых стратегий."""

    def __init__(self):
        """Инициализирует параметры подключения к бд."""
        self.conn = None
        self.db_path = self._get_db_path()

    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("PRAGMA foreign_keys = ON")
        return self

    async def __aexit__(self, *args):
        try:
            await self.conn.close()
        except Exception as e:
            logger.error("Ошибка при закрытии соединения: %s", e)
            raise

    @staticmethod
    def _get_db_path() -> Path:
        """Возвращает путь к файлу базы данных."""
        path_dir = Path.cwd() / "database"
        path_dir.mkdir(parents=True, exist_ok=True)
        return path_dir / "trading_strategy_tester.db"

    @staticmethod
    async def _table_exists(cursor: aiosqlite.Cursor, table_name: str) -> bool:
        """Проверяет существование таблицы в базе данных."""
        try:
            await cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return await cursor.fetchone() is not None
        except aiosqlite.Error as e:
            logger.error("Ошибка проверки существования таблицы: %s", e)
            raise

    @staticmethod
    async def _clear_table(cursor: aiosqlite.Cursor, table_name: str) -> None:
        """Очищает таблицу, если она существует."""
        if await DatabaseGateway._table_exists(cursor, table_name):
            await cursor.execute(f"DELETE FROM {table_name}")
            await cursor.execute(
                    f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"
            )

    async def saves_candles(self, candles: List[StockCandle], ticker: str,
                            clear_existing: bool = True) -> Path:
        """Сохраняет свечи в базу данных.

        Args:
            candles: Список датаклассов хранящих данные свечей акции.
            ticker: Тикер акции.

        Returns:
            Путь к базе данных.

        Raises:
            ValueError: Если таблица не существует.
            sqlite3.Error: При ошибках работы с БД.
        """
        if not candles:
            raise ValueError("Список свечей не может быть пустым")

        table_name = f"{ticker.lower()}_dataframe"

        try:
            async with self.conn.cursor() as cursor:
                await self.conn.execute("BEGIN TRANSACTION")

                if clear_existing:
                    # Полное пересоздание таблицы вместо очистки
                    await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    logger.debug("Таблица %s удалена для пересоздания",
                                 table_name)

                await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    open TEXT NOT NULL,
                    close TEXT NOT NULL,
                    high TEXT NOT NULL,
                    low TEXT NOT NULL,
                    value TEXT NOT NULL,
                    volume TEXT NOT NULL,
                    begin TIMESTAMP NOT NULL,
                    end TIMESTAMP NOT NULL,
                    UNIQUE(begin, end) ON CONFLICT REPLACE
                )
                """)

                await cursor.executemany(
                    f"""INSERT INTO {table_name}
                    (open, close, high, low, value, volume, begin, end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (
                            str(candle.open),
                            str(candle.close),
                            str(candle.high),
                            str(candle.low),
                            str(candle.value),
                            str(candle.volume),
                            candle.begin.to_pydatetime(),
                            candle.end.to_pydatetime()
                        )
                        for candle in candles
                    ]
                )
                await self.conn.commit()
                logger.info("Сохранено %s датафреймов в %s", len(candles),
                            table_name)

        except aiosqlite.Error as e:
            await self.conn.rollback()
            logger.error("Ошибка сохранения датафреймов: %s", e)
            raise

        return self._get_db_path()

    async def saves_results(self, results: List[TradingResult], ticker: str,
                            clear_existing: bool = True) -> Path:
        """
        Сохраняет результаты в базу данных с возможностью дублирования дат.

        Args:
            results: Список датаклассов хранящих данные результатов торговой
                стратегии на конкретную дату.
            ticker: Тикер акции.

        Returns:
            filepath: Путь к базе данных.

        Raises:
            ValueError: Если таблица не существует.
            sqlite3.Error: При ошибках работы с БД.
        """
        if not results:
            raise ValueError("Список свечей не может быть пустым")

        table_name = f"{ticker.lower()}_results"

        try:
            async with self.conn.cursor() as cursor:
                await self.conn.execute("BEGIN TRANSACTION")

                if clear_existing:
                    # Полное пересоздание таблицы вместо очистки
                    await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    logger.debug("Таблица %s удалена для пересоздания",
                                 table_name)

                await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_str TEXT NOT NULL,
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
                logger.debug("Таблица %s создана/проверена", table_name)

                await cursor.executemany(
                    f"""INSERT INTO {table_name}
                    (date_str, max_price, min_price, cache, share_count,
                    amount_in_shares, overall_result, comiss_sum, tax_sum,
                    total_tax)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (
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
                        for result in results
                    ]
                )
                await self.conn.commit()
                logger.info("Сохранено %s записей в %s", len(results),
                            table_name)

        except aiosqlite.Error as e:
            await self.conn.rollback()
            logger.error("Ошибка сохранения результатов: %s", e)
            raise

        return self._get_db_path()

    async def saves_calculations(self, results: Dict[str, any],
                                 ticker: str) -> Path:
        """Сохраняет результаты расчетов в базу данных.

        Args:
            results: Словарь с результатами расчетов торговой сратегии.
            ticker: Тикер акции.

        Returns:
            filepath: Путь к базе данных.

        Raises:
            ValueError: Если таблица не существует.
            sqlite3.Error: При ошибках работы с БД.
        """
        if not results:
            raise ValueError("Список свечей не может быть пустым")

        table_name = f"{ticker.lower()}_calculations"

        data = (
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
        )

        try:
            async with self.conn.cursor() as cursor:
                await self.conn.execute("BEGIN TRANSACTION")

                await cursor.execute(f"""
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

                await cursor.execute(
                    f"""INSERT INTO {table_name} (
                    start_date, end_date, initial_cache, buy_price,
                    sell_price, buy_count, sell_count, comission_percent,
                    tax_percent, invest_period_days, invest_period_years,
                    total_income_sum, total_income_perc, incom_year_sum,
                    incom_year_pers, accumulated_commission, final_cache,
                    final_amount_in_shares, final_overall_result, total_tax
                    )
                    VALUES ({','.join(['?'] * 20)})""", data)
                await self.conn.commit()
                logger.info("Сохранение расчетов в %s", table_name)

        except aiosqlite.Error as e:
            await self.conn.rollback()
            logger.error("Ошибка сохранения в saves_calculations: %s", e)
            raise

        return self._get_db_path()

    async def load_dataframe_history(self, ticker: str) -> List[StockCandle]:
        """
        Загружает данные свечей из базы данных.

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
            async with self.conn.cursor() as cursor:

                if not await self._table_exists(cursor, table_name):
                    raise ValueError(
                        f"Таблица {table_name} не найдена в базе данных"
                    )

                await cursor.execute(f"""
                    SELECT open, close, high, low, value, volume,
                    begin, end
                    FROM {table_name}
                    ORDER BY begin
                    """)

                # Получение всех строк
                rows = await cursor.fetchall()

                return [
                    StockCandle(
                        open=Decimal(row[0]),
                        close=Decimal(row[1]),
                        high=Decimal(row[2]),
                        low=Decimal(row[3]),
                        value=Decimal(row[4]),
                        volume=Decimal(row[5]),
                        begin=str(row[6]),
                        end=str(row[7])
                    )
                    for row in rows
                ]

        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Ошибка при загрузке данных: {e}")

    async def load_strategy_results(self, ticker: str) -> List[dict]:
        """
        Загружает результаты торговой стратегии из таблицы результатов.

        Args:
            ticker: Тикер акции (например: 'GAZP')

        Returns:
            List[dict]: Список словарей с результатами по дням
                       в формате TradingResult

        Raises:
            ValueError: Если таблица не существует
            sqlite3.Error: При ошибках БД
        """
        table_name = f"{ticker.lower()}_results"

        try:
            async with self.conn.cursor() as cursor:

                if not await self._table_exists(cursor, table_name):
                    raise ValueError(
                        f"Таблица {table_name} не найдена в базе данных"
                    )

                await cursor.execute(f"""
                    SELECT date_str, max_price, min_price, cache,
                           share_count, amount_in_shares, overall_result,
                           comiss_sum, tax_sum, total_tax
                    FROM {table_name}
                    ORDER BY date_str
                    """)

                columns = [col[0] for col in cursor.description]
                rows = await cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]

        except aiosqlite.Error as e:
            raise aiosqlite.Error(f"Ошибка загрузки результатов: {e}")
