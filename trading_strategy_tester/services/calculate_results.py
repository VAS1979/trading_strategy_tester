""" Содержит класс, который рассчитывает
итоговые финансовые результаты стратегии. """

from datetime import datetime
from typing import Dict, List
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)


class CalculateResult:
    """ Класс, для рассчита итогов финансовых результатов стратегии."""

    def __init__(self):
        """Инициализация точности вычислений."""
        getcontext().prec = 8

    @classmethod
    def round_money(cls, value: Decimal) -> Decimal:
        """Унифицированное округление денежных величин
        с банковским округлением.
        """

        return value.quantize(Decimal("1.00"), ROUND_HALF_EVEN)

    def calculates_results(self, data: List[TradingResult],
                           param: StrategyParameters,
                           transactions: List[int]) -> Dict[str, any]:
        """ Рассчитывает итоговые финансовые результаты стратегии.

        Args:
            data (List[TradingResult]): Список данных результатов торговой
                стратегии на конкретную дату.
            param StrategyParameters: Параметры стратегии.
            transactions: List[int]: Количество сделок.

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
            # Преобразование дат
            start_date = datetime.strptime(data[0].date_str, '%Y-%m-%d')
            end_date = datetime.strptime(data[-1].date_str, '%Y-%m-%d')

            # Расчет периода инвестирования
            invest_period_days = Decimal((end_date - start_date).days)
            invest_period_years = self.round_money(invest_period_days / 365)

            # Расчет доходности
            initial_result = Decimal(str(data[0].overall_result))
            final_result = Decimal(str(data[-1].overall_result))
            total_income_sum = self.round_money(final_result - initial_result)
            total_income_perc = self.round_money(
                ((final_result - initial_result) / initial_result * 100))

            # Годовая доходность
            incom_year_sum = self.round_money(
                total_income_sum / invest_period_years)
            incom_year_pers = self.round_money(
                total_income_perc / invest_period_years)

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
