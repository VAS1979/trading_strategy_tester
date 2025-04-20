""" Содержит класс, который рассчитывает
итоговые финансовые результаты стратегии. """

from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal, getcontext
from typing import Any

from trading_strategy_tester.api.schemas import StrategyParameters
from trading_strategy_tester.models.trading_result import TradingResult
from trading_strategy_tester.utils.logger import logging

logger = logging.getLogger(__name__)

getcontext().prec = 8


class CalculateResult:
    """Класс, для рассчита итогов финансовых результатов стратегии."""

    @classmethod
    def round_money(cls, value: Decimal) -> Decimal:
        """Унифицированное округление денежных величин
        с банковским округлением.
        """

        return value.quantize(Decimal("1.00"), ROUND_HALF_EVEN)

    def calculates_results(
        self, data: list[TradingResult], param: StrategyParameters, transactions: list[int]
    ) -> dict[str, Any]:
        """Рассчитывает итоговые финансовые результаты стратегии.

        Args:
            data (List[TradingResult]): Список данных результатов торговой
                стратегии на конкретную дату.
            param StrategyParameters: Параметры стратегии.
            transactions: List[int]: Количество сделок.

        Returns:
            Dict[str, any]: Словарь с результатами расчетов:
                start_date: Дата начала инвестирования.
                end_date: Дата завершения инвестрирования.
                invest_period_days: Период инвестирования в днях.
                invest_period_years: Период инвестирования в годах.
                total_income_sum: Суммарный доход сумма.
                total_income_perc: Суммарный доход в процентах.
                incom_year_sum: Средний доход в год в сумме.
                incom_year_pers: Средний доход в год в процентах.
                initial_cache: Начальная сумма кэша.
                buy_price: Цена покупки по условию стратегии.
                sell_price: Цена продажи по условию стратегии.
                buy_count: Количество сделок покупки.
                sell_count: Количество сделок продаж.
                comission_percent: Процентная ставка комиссии брокера.
                tax_percent: Процентная ставка налога.
                accumulated_commission: Сумма комиссии за весь период.
                total_tax: Общая сумма налога за весь период.
                final_cache: Итоговая сумма в кэше.
                final_amount_in_shares: Итоговая сумма в акциях.
                final_overall_result: Общая итоговая сумма.

        Raises:
            ValueError: Если данные не могут быть корректно обработаны.
            TypeError: Если тип данных не соответствует ожидаемому.
            ZeroDivisionError: Если происходит деление на ноль.
        """

        results = {}

        # Блок обработки дат
        try:
            start_date = datetime.strptime(data[0].date_str, "%Y-%m-%d")
            end_date = datetime.strptime(data[-1].date_str, "%Y-%m-%d")
            results.update({"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")})
        except (ValueError, IndexError) as e:
            logger.exception("Ошибка при обработке дат: %s", e)
            raise ValueError("Некорректные данные дат") from e

        # Блок расчета периода инвестирования
        try:
            invest_period_days = Decimal((end_date - start_date).days + 1)
            invest_period_years = CalculateResult.round_money(invest_period_days / 365)
            #    print('invest_period_days', invest_period_days)
            #    print('invest_period_years', invest_period_years)
            results.update({"invest_period_days": invest_period_days, "invest_period_years": invest_period_years})  # type: ignore
        except (TypeError, ValueError) as e:
            logger.exception("Ошибка при расчете периода " "инвестирования: %s", e)
            raise ValueError("Ошибка расчета периода инвестирования") from e

        # Блок расчета доходности
        try:
            initial_result = Decimal(str(data[0].overall_result))
            final_result = Decimal(str(data[-1].overall_result))
            total_income_sum = CalculateResult.round_money(final_result - initial_result)
            total_income_perc = CalculateResult.round_money((final_result - initial_result) / initial_result * 100)

            results.update({"total_income_sum": total_income_sum, "total_income_perc": total_income_perc})  # type: ignore
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.exception("Ошибка при расчете доходности: %s", e)
            if isinstance(e, ZeroDivisionError):
                raise ZeroDivisionError("Деление на ноль при расчете доходности") from e
            raise ValueError("Ошибка расчета доходности") from e

        # Блок расчета годовой доходности
        try:
            incom_year_sum = CalculateResult.round_money(total_income_sum / invest_period_years)
            incom_year_pers = CalculateResult.round_money(total_income_perc / invest_period_years)

            results.update({"incom_year_sum": incom_year_sum, "incom_year_pers": incom_year_pers})  # type: ignore
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.exception("Ошибка при расчете годовой доходности: %s", e)
            if isinstance(e, ZeroDivisionError):
                raise ZeroDivisionError("Деление на ноль при расчете годовой доходности") from e
            raise ValueError("Ошибка расчета годовой доходности") from e

        # Блок сбора финальных данных
        try:
            results.update(
                {
                    "initial_cache": param.initial_cache,  # type: ignore
                    "buy_price": param.buy_price,  # type: ignore
                    "sell_price": param.sell_price,  # type: ignore
                    "buy_count": transactions[0],  # type: ignore
                    "sell_count": transactions[1],  # type: ignore
                    "comission_percent": param.commission_rate,  # type: ignore
                    "tax_percent": param.tax_rate,  # type: ignore
                    "accumulated_commission": data[-1].comiss_sum,  # type: ignore
                    "total_tax": data[-1].total_tax,  # type: ignore
                    "final_cache": data[-1].cache,  # type: ignore
                    "final_amount_in_shares": data[-1].amount_in_shares,  # type: ignore
                    "final_overall_result": data[-1].overall_result,  # type: ignore
                }
            )
        except (AttributeError, IndexError, TypeError) as e:
            logger.exception("Ошибка при сборе финальных данных: %s", e)
            raise ValueError("Ошибка сбора финальных данных") from e

        return results
