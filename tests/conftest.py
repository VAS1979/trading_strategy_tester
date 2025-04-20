""" Содержит фикстуры для тестов. """

import pytest

from trading_strategy_tester.models.strategy_parameters import StrategyParameters
from trading_strategy_tester.models.trading_data import TradingData
from trading_strategy_tester.models.trading_result import TradingResult


@pytest.fixture
def sample_csv_data():
    """Фикстура, возвращающая CSV-строку с тестовыми данными."""

    return """open,close,high,low,value,volume,begin,end
322.19,315.02,325.45,313.66,505130903.3,1595690.0,2014-01-06,2014-01-06 23:59:59
315.51,314.63,317.95,311.6,361992311.1,1150950.0,2014-01-08,2014-01-08 23:59:59
"""


@pytest.fixture
def strategy_parameters():
    """Фикстура для создания параметров стратегии."""
    return StrategyParameters(
        initial_cache=10000.0, buy_price=100.0, sell_price=150.0, commission_rate=0.01, tax_rate=0.13
    )


@pytest.fixture
def trading_data():
    """Фикстура для создания данных о торговых днях."""
    return [
        TradingData(date="2023-01-01", high=120.0, low=90.0, close=110.0),
        TradingData(date="2023-01-02", high=130.0, low=100.0, close=120.0),
        TradingData(date="2023-01-03", high=140.0, low=110.0, close=130.0),
        TradingData(date="2023-01-04", high=160.0, low=120.0, close=150.0),
        TradingData(date="2023-01-05", high=170.0, low=130.0, close=160.0),
    ]


@pytest.fixture
def expected_results():
    """Фикстура для создания ожидаемых результатов."""
    return [
        TradingResult(
            date_str="2023-01-01",
            max_price=120.0,
            min_price=90.0,
            cache=8900.0,
            share_count=10,
            amount_in_shares=1100.0,
            overall_result=10000.0,
            comiss_sum=100.0,
            tax_sum=0.0,
            total_tax=0.0,
        ),
        TradingResult(
            date_str="2023-01-02",
            max_price=130.0,
            min_price=100.0,
            cache=8900.0,
            share_count=10,
            amount_in_shares=1200.0,
            overall_result=10100.0,
            comiss_sum=100.0,
            tax_sum=0.0,
            total_tax=0.0,
        ),
        TradingResult(
            date_str="2023-01-03",
            max_price=140.0,
            min_price=110.0,
            cache=8900.0,
            share_count=10,
            amount_in_shares=1300.0,
            overall_result=10200.0,
            comiss_sum=100.0,
            tax_sum=0.0,
            total_tax=0.0,
        ),
        TradingResult(
            date_str="2023-01-04",
            max_price=160.0,
            min_price=120.0,
            cache=10350.0,
            share_count=0,
            amount_in_shares=0.0,
            overall_result=10350.0,
            comiss_sum=250.0,
            tax_sum=65.0,
            total_tax=65.0,
        ),
        TradingResult(
            date_str="2023-01-05",
            max_price=170.0,
            min_price=130.0,
            cache=10350.0,
            share_count=0,
            amount_in_shares=0.0,
            overall_result=10350.0,
            comiss_sum=250.0,
            tax_sum=0.0,
            total_tax=65.0,
        ),
    ]


@pytest.fixture
def expected_transactions():
    """Фикстура для создания ожидаемых транзакций."""
    return [1, 1]
