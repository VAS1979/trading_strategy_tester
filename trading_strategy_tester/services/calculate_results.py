""" Содержит класс, который рассчитывает
итоговые финансовые результаты стратегии и выгружает их в JSON файл. """

from datetime import datetime
from typing import Dict, List
from trading_strategy_tester.models.strategy_parameters import (
    StrategyParameters)
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class CalculateResult:
    """ Класс, для рассчита итогов финансовых результатов стратегии."""

    def calculates_results(self, data: List[TradingResult],
                           param: StrategyParameters,
                           transactions: List[int]) -> Dict[str, any]:
        """ Рассчитывает итоговые финансовые результаты стратегии.

        Args:

        Variables:
            start_date: Дата начала инвестирования.
            end_date: Дата завершения инвестрирования.
            initial_cache: Начальная сумма кэша.
            buy_price: Цена покупки по условию стратегии.
            sell_price: Цена продажи по условию стратегии.
            buy_count: Количество сделок покупки.
            sell_count: Количество сделок продаж.
            comission_percent: Процентная ставка комиссии брокера.
            tax_percent: Процентная ставка налога.
            invest_period_days: Период инвестирования в днях.
            invest_period_years: Период инвестирования в годах.
            total_income_sum: Суммарный доход сумма.
            total_income_perc: Суммарный доход в процентах.
            incom_year_sum: Средний доход в год в сумме.
            incom_year_pers: Средний доход в год в процентах.
            accumulated_commission: Сумма комиссии за весь период.
            final_cache: Итоговая сумма в кэше.
            final_amount_in_shares: Итоговая сумма в акциях.
            final_overall_result: Общая итоговая сумма.
            total_tax: Общая сумма налога за весь период.
        """

        try:
            start_date = datetime.strptime(data[0].date_str, '%Y-%m-%d')
            end_date = datetime.strptime(data[-1].date_str, '%Y-%m-%d')

            invest_period_days = (end_date - start_date).days
            invest_period_years = round(invest_period_days / 365, 2)

            total_income_sum = round((data[0].overall_result -
                                      data[-1].overall_result), 2) * -1
            total_income_perc = round(data[-1].overall_result /
                                      data[0].overall_result * 100, 2)

            incom_year_sum = round(total_income_sum / invest_period_years, 2)
            incom_year_pers = round(total_income_perc / invest_period_years, 2)

            accumulated_commission = data[-1].comiss_sum
            total_tax = data[-1].total_tax
            final_cache = data[-1].cache
            final_amount_in_shares = data[-1].amount_in_shares
            final_overall_result = data[-1].overall_result

            results = {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "initial_cache": param.initial_cache,
                    "buy_price": param.buy_price,
                    "sell_price": param.sell_price,
                    "buy_count": transactions[0],
                    "sell_count": transactions[1],
                    "comission_percent": param.commission_rate,
                    "tax_percent": param.tax_rate,
                    "invest_period_days": invest_period_days,
                    "invest_period_years": invest_period_years,
                    "total_income_sum": total_income_sum,
                    "total_income_perc": total_income_perc,
                    "incom_year_sum": incom_year_sum,
                    "incom_year_pers": incom_year_pers,
                    "accumulated_commission": accumulated_commission,
                    "final_cache": final_cache,
                    "final_amount_in_shares": final_amount_in_shares,
                    "final_overall_result": final_overall_result,
                    "total_tax": total_tax
                }

            return results

        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.exception("Ошибка при расчете результатов: %s", e)
            raise
