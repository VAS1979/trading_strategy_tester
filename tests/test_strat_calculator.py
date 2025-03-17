""" . """

from trading_strategy_tester.services.strategy_calculator import (
    StrategyCalculator)


def test_strategy_calculator(strategy_parameters, trading_data,
                             expected_results, expected_transactions):
    """Тест для проверки корректности расчета стратегии."""

    calculator = StrategyCalculator(strategy_parameters)
    results, transactions = calculator.calculates_data(trading_data)

    # Проверка количества транзакций
    assert transactions == expected_transactions

    # Проверка результатов по дням
    for i, result in enumerate(results):
        assert result.date_str == expected_results[i].date_str
        assert result.max_price == expected_results[i].max_price
        assert result.min_price == expected_results[i].min_price
        assert result.cache == expected_results[i].cache
        assert result.share_count == expected_results[i].share_count
        assert result.amount_in_shares == expected_results[i].amount_in_shares
        assert result.overall_result == expected_results[i].overall_result
        assert result.comiss_sum == expected_results[i].comiss_sum
        assert result.tax_sum == expected_results[i].tax_sum
        assert result.total_tax == expected_results[i].total_tax


def test_strategy_calculator_with_empty_data(strategy_parameters):
    """Тест для проверки обработки пустых данных."""
    calculator = StrategyCalculator(strategy_parameters)
    results, transactions = calculator.calculates_data([])

    assert results == []
    assert transactions == []


def test_strategy_calculator_with_none_data(strategy_parameters):
    """Тест для проверки обработки данных, равных None."""
    calculator = StrategyCalculator(strategy_parameters)
    results, transactions = calculator.calculates_data(None)

    assert results == []
    assert transactions == []
