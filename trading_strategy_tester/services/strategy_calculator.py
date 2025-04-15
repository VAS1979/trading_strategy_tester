""" Содержит класс, моделирующий торговые операции на
каждый торговый день по стратегии. """

from datetime import datetime
from typing import List, Tuple
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

from trading_strategy_tester.models.stock_candle import StockCandle
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.utils.logger import logging

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
        """

        self.parameters = parameters
        getcontext().prec = 10

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

    def calculates_data(self, data: List[StockCandle]
                        ) -> Tuple[List[TradingResult], List[int]]:
        """
        Рассчитывает результаты торговой стратегии.

        Args:
            data (List[StockCandle]): Список данных о торговых днях.

        Variables:
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
            count: (Decimal): Времененная величина для расчета
                количества акций.
            date_str (str): Дата.

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

        try:
            share_count = 0
            amount_in_shares = Decimal('0')
            overall_result = Decimal('0')
            buy_count = 0
            sell_count = 0
            comiss_sum = Decimal('0')
            tax_sum = Decimal('0')
            total_tax = Decimal('0')
            data_list = []
            years_list = []

            cache = self.parameters.initial_cache
            buy_price = self.parameters.buy_price
            sell_price = self.parameters.sell_price
            commission_rate = self.parameters.commission_rate
            tax_rate = self.parameters.tax_rate

            price_differ = sell_price - buy_price

            for row in data:
                closing_price = row.close
                max_price = row.high
                min_price = row.low
                date_str = row.begin.split()[0]
                current_date = datetime.strptime(date_str, '%Y-%m-%d')

                # Логика обработки покупок
                if cache >= buy_price and buy_price >= min_price:
                    count = int(cache // buy_price)
                    comiss_tmp = count * buy_price * commission_rate
                    # Если сумма сделки + комиссия > кэша
                    if cache < count * buy_price + comiss_tmp:
                        while (
                            count > 0
                            and cache < count * buy_price + comiss_tmp
                        ):
                            count -= 1
                        comiss_tmp = count * buy_price * commission_rate
                    comiss_sum += comiss_tmp
                    cache = cache - count * buy_price - comiss_tmp
                    share_count += count
                    buy_count += 1

                # Логика обработки продаж
                tax_tmp = Decimal('0')

                if max_price >= sell_price and share_count > 0:
                    comiss_tmp = share_count * sell_price * commission_rate
                    cache = cache + share_count * sell_price - comiss_tmp
                    tax_tmp = price_differ * share_count * tax_rate
                    tax_tmp = self.round_money(tax_tmp)
                    share_count = 0
                    sell_count += 1
                    comiss_sum += comiss_tmp

                # Завершающая обработка
                amount_in_shares = share_count * closing_price
                overall_result = amount_in_shares + cache
                tax_sum = tax_sum + tax_tmp
                total_tax += tax_tmp

                # Снятие налога в конце года
                year = current_date.year
                month = current_date.month
                day = current_date.day
                if (
                    year not in years_list
                    and month == 12
                    and 20 <= day <= 31
                ):
                    years_list.append(year)
                    cache -= tax_sum
                    tax_sum = Decimal('0')

                # Округление результатов
                max_price = self.round_money(max_price)
                min_price = self.round_money(min_price)
                cache = self.round_money(cache)
                comiss_sum = self.round_money(comiss_sum)
                amount_in_shares = self.round_money(amount_in_shares)
                overall_result = self.round_money(overall_result)
                total_tax = self.round_money(total_tax)

                result = TradingResult(
                    date_str,
                    max_price,
                    min_price,
                    cache,
                    share_count,
                    amount_in_shares,
                    overall_result,
                    comiss_sum,
                    tax_sum,
                    total_tax
                )
                data_list.append(result)

            # Вычет налога в конце срока, если он не в конце декабря
            last_result = data_list[-1]
            last_result.cache -= last_result.tax_sum
            last_result.tax_sum = Decimal('0')

            counting_transactions = [buy_count, sell_count]
            logger.info("Расчет результатов торговой стратегии...")

            return data_list, counting_transactions

        except Exception as e:
            logger.error("Произошла общая ошибка: %s", e)
            return [], []
