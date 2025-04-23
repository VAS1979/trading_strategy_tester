"""
Содержит класс, моделирующий торговые операции на
каждый торговый день по стратегии.
"""

import logging
from datetime import datetime
from typing import List, Tuple
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

from trading_strategy_tester.models.stock_candle import StockCandle
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.api.schemas import StrategyParameters

logger = logging.getLogger(__name__)


class StrategyCalculator:
    """
    Класс для расчета торговой стратегии.
    """

    # Константы класса
    MONEY_PRECISION = Decimal('0.01')
    ROUNDING_METHOD = ROUND_HALF_EVEN

    def __init__(self, parameters: StrategyParameters):
        """
        Инициализация класса StrategyCalculator.

        Args:
            parameters (StrategyParameters): Параметры стратегии.
            share_count (int): Количество приобретенных акций.
            amount_in_shares (Decimal): Текущая стоимость всех купленных акций.
            overall_result (Decimal): Общий результат (стоимость акций + кэш).
            buy_count (int): Количество покупок.
            sell_count (int): Количество продаж.
            comiss_sum (Decimal): Сумма комиссии по нарастающей.
            tax_sum (Decimal): Сумма налога за текущий год по нарастающей.
            total_tax (Decimal): Общая сумма налога за весь
                период по нарастающей
            years_list (list): Сюда вносится год, после вычета налога, в конце
                года, для исключения повторного списания.
            cache (Decimal): Сумма кэша.
        """
        self.parameters = parameters
        getcontext().prec = 10

        self.share_count = 0
        self.amount_in_shares = Decimal('0')
        self.overall_result = Decimal('0')
        self.buy_count = 0
        self.sell_count = 0
        self.comiss_sum = Decimal('0')
        self.tax_sum = Decimal('0')
        self.total_tax = Decimal('0')
        self.data_list = []
        self.years_list = []
        self.cache = self.parameters.initial_cache

    @classmethod
    def round_money(cls, value: Decimal) -> Decimal:
        """Унифицированное округление денежных величин.

        Args:
            value: Значение для округления в Decimal.

        Returns:
            Округленное значение с банковским округлением.
        """
        return value.quantize(cls.MONEY_PRECISION,
                              rounding=cls.ROUNDING_METHOD)

    def _process_buy(self, min_price: Decimal) -> bool:
        """
        Обработка логики покупки акций.

        Args:
            min_price: Минимальная цена за день.

        Variables:
            buy_price (Decimal): Цена покупки акций.
            commission_rate (Decimal): Процентая ставка комиссии брокера.
            count (int): Временная величина количество акций.
            comiss_tmp (Decimal): Временная величина для расчета налога.

        Returns:
            bool: Была ли совершена покупка.
        """
        buy_price = self.parameters.buy_price
        commission_rate = self.parameters.commission_rate

        if self.cache >= buy_price and buy_price >= min_price:
            count = int(self.cache // buy_price)
            comiss_tmp = count * buy_price * commission_rate

            # Если сумма сделки + комиссия > кэша
            if self.cache < count * buy_price + comiss_tmp:
                while (
                    count > 0
                    and self.cache < count * buy_price + comiss_tmp
                ):
                    count -= 1
                comiss_tmp = count * buy_price * commission_rate

            self.comiss_sum += comiss_tmp
            self.cache = self.cache - count * buy_price - comiss_tmp
            self.share_count += count
            self.buy_count += 1

    def _process_sell(self, max_price: Decimal) -> Decimal:
        """
        Обработка логики продажи акций.

        Args:
            max_price: Максимальная цена за день.

        Variables:
            sell_price (Decimal): Цена продажи акций.
            commission_rate (Decimal): Процентая ставка комиссии брокера.
            tax_rate (Decimal): Налоговая ставка.
            tax_tmp (Decimal): Временная величина для расчета налога.
            comiss_tmp (Decimal): Временная величина для расчета налога.

        Returns:
            Decimal: Сумма налога от сделки.
        """
        sell_price = self.parameters.sell_price
        commission_rate = self.parameters.commission_rate
        tax_rate = self.parameters.tax_rate
        tax_tmp = Decimal('0')

        if max_price >= sell_price and self.share_count > 0:
            comiss_tmp = self.share_count * sell_price * commission_rate
            self.cache += self.share_count * sell_price - comiss_tmp

            price_differ = sell_price - self.parameters.buy_price
            tax_tmp = self.round_money(
                price_differ * self.share_count * tax_rate)

            self.share_count = 0
            self.sell_count += 1
            self.comiss_sum += comiss_tmp

        return tax_tmp

    def _process_year_end_tax(self, current_date: datetime):
        """
        Обработка налогов в конце года.
        """
        year = current_date.year
        month = current_date.month
        day = current_date.day

        if (
            year not in self.years_list
            and month == 12
            and 20 <= day <= 31
        ):
            self.years_list.append(year)
            self.cache -= self.tax_sum
            self.tax_sum = Decimal('0')

    def _create_trading_result(self, row: StockCandle,
                               tax_tmp: Decimal) -> TradingResult:
        """
        Создание объекта TradingResult для текущего дня.
        """
        closing_price = row.close
        date_str = row.begin.split()[0]

        self.amount_in_shares = self.share_count * closing_price
        self.overall_result = self.amount_in_shares + self.cache
        self.tax_sum += tax_tmp
        self.total_tax += tax_tmp

        # Округление всех значений
        rounded_values = {
            "max_price": self.round_money(row.high),
            "min_price": self.round_money(row.low),
            "cache": self.round_money(self.cache),
            "comiss_sum": self.round_money(self.comiss_sum),
            "amount_in_shares": self.round_money(self.amount_in_shares),
            "overall_result": self.round_money(self.overall_result),
            "total_tax": self.round_money(self.total_tax),
            "tax_sum": self.round_money(self.tax_sum)
        }

        return TradingResult(
            date_str=date_str,
            share_count=self.share_count,
            **rounded_values
        )

    def calculates_data(self, data: List[StockCandle]
                        ) -> Tuple[List[TradingResult], List[int]]:
        """
        Рассчитывает результаты торговой стратегии.

        Args:
            data (List[StockCandle]): Список данных о торговых днях.

        Returns:
            Tuple[List[TradingResult], List[int]]:
            data_list: Список списков, каждый из которых описывает состояние
             торгового портфеля на определённую дату: [date_str, max_price,
             min_price, cache, share_count, amount_in_shares, overall_result,
             comiss_sum, tax_sum, total_tax].
            counting_transactions: Список сделок [buy_count, sell_count].
        """
        if data is None:
            logger.error("Входные данные равны None.")
            return [], []

        for row in data:
            current_date = datetime.strptime(row.begin.split()[0], '%Y-%m-%d')
            tax_tmp = Decimal('0')

            # Определяем возможные операции
            can_buy = (self.cache >= self.parameters.buy_price and
                       self.parameters.buy_price >= row.low)
            can_sell = (self.parameters.sell_price <= row.high and
                        self.share_count > 0)

            # Флаг проверки на наличие сделок на текущий день.
            transaction = False

            # Сценарий 1: Покупка новых акций
            if can_buy:
                self._process_buy(row.low)
                result = self._create_trading_result(row, Decimal('0'))
                self.data_list.append(result)
                transaction = True

                # После покупки проверяем возможность продажи
                if (
                    self.parameters.sell_price <= row.high
                    and self.share_count > 0
                ):
                    tax_tmp = self._process_sell(row.high)
                    result = self._create_trading_result(row, tax_tmp)
                    self.data_list.append(result)

            # Сценарий 2: Продажа существующих акций
            if can_sell:
                tax_tmp = self._process_sell(row.high)
                result = self._create_trading_result(row, tax_tmp)
                self.data_list.append(result)
                transaction = True

                # После продажи проверяем возможность покупки
                can_buy = (self.cache >= self.parameters.buy_price and
                           self.parameters.buy_price >= row.low)

            # Сценарий 3: Если не было операций
            elif not transaction:
                result = self._create_trading_result(row, tax_tmp)
                self.data_list.append(result)

            # Обработка налогов в конце года
            self._process_year_end_tax(current_date)

        # Вычет налога в конце периода, если не в конце декабря
        if self.data_list:
            last_result = self.data_list[-1]
            last_result.cache -= last_result.tax_sum
            last_result.tax_sum = Decimal('0')

        counting_transactions = [self.buy_count, self.sell_count]
        logger.info("Расчет результатов торговой стратегии...")

        return self.data_list, counting_transactions
