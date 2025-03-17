""" Содержит класс расчета торговой стратегии. """

from datetime import datetime
from typing import List, Tuple
from trading_strategy_tester.models.trading_data import TradingData
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.models.strategy_parameters import (
    StrategyParameters)
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class StrategyCalculator:
    """
    Класс для расчета торговой стратегии.
    """

    def __init__(self, parameters: StrategyParameters):
        """
        Инициализация класса StrategyCalculator.

        Args:
            parameters (StrategyParameters): Параметры стратегии.
        """

        self.parameters = parameters

    def calculates_data(self, data: List[TradingData]
                        ) -> Tuple[List[TradingResult], List[int]]:
        """
        Рассчитывает результаты торговой стратегии.

        Args:
            data (List[TradingData]): Список данных о торговых днях.

        Variables:
            share_count (int): Количество приобретенных акций.
            amount_in_shares (float): Текущая стоимость всех купленных акций.
            overall_result (float): Общий результат (стоимость акций + кэш).
            buy_count (int): Количество покупок.
            sell_count (int): Количество продаж.
            comiss_sum (float): Сумма комиссии по нарастающей.
            tax_sum (float): Сумма налога за текущий год по нарастающей.
            total_tax (float): Общая сумма налога за весь период по нарастающей
            years_list (list): Сюда вносится год, после вычета налога, в конце
                года, для исключения повторного списания.
            count: (float): Времененная величина для расчета количества акций.
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
            amount_in_shares = 0
            overall_result = 0
            buy_count = 0
            sell_count = 0
            comiss_sum = 0
            tax_sum = 0
            total_tax = 0
            data_list = []
            years_list = []

            cache = self.parameters.initial_cache
            buy_price = self.parameters.buy_price
            sell_price = self.parameters.sell_price
            commission_rate = self.parameters.commission_rate
            tax_rate = self.parameters.tax_rate

            price_differ = sell_price - buy_price

            for row in data:
                date_str = row.date
                max_price = row.high
                min_price = row.low
                closing_price = row.close
                current_date = datetime.strptime(date_str, '%Y-%m-%d')

                try:
                    # Логика обработки покупок
                    if cache >= buy_price and buy_price >= min_price:
                        count = int(cache // buy_price)
                        comiss_tmp = count * buy_price * commission_rate
                        # Если сумма сделки + комиссия > кэша
                        if cache < count * buy_price + comiss_tmp:
                            while count * buy_price + comiss_tmp > cache:
                                count -= 1
                            comiss_tmp = count * buy_price * commission_rate
                        comiss_sum += comiss_tmp
                        cache = cache - count * buy_price - comiss_tmp
                        share_count += count
                        buy_count += 1

                    # Логика обработки продаж
                    tax_tmp = 0

                    if max_price >= sell_price and share_count > 0:
                        comiss_tmp = share_count * sell_price * commission_rate
                        cache = cache + share_count * sell_price - comiss_tmp
                        tax_tmp = round(price_differ * share_count
                                        * tax_rate, 2)
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
                        tax_sum = 0

                    # Округление результатов
                    cache = round(cache, 2)
                    comiss_sum = round(comiss_sum, 2)
                    amount_in_shares = round(amount_in_shares, 2)
                    overall_result = round(overall_result, 2)
                    total_tax = round(total_tax, 2)

                    res = TradingResult(date_str, max_price, min_price, cache,
                                        share_count, amount_in_shares,
                                        overall_result, comiss_sum, tax_sum,
                                        total_tax)
                    data_list.append(res)

                except KeyError as e:
                    logger.error("Столбец %s не найден в строке: %s", e, row)
                    raise

            # Вычет налога в конце срока, если он не в конце декабря
            data_list[-1].cache -= data_list[-1].tax_sum
            data_list[-1].tax_sum = 0

            counting_transactions = [buy_count, sell_count]
            logger.info("Рассчет результатов торговой стратегии...")
            return data_list, counting_transactions

        except Exception as e:
            logger.error("Произошла общая ошибка: %s", e)
            return [], []
