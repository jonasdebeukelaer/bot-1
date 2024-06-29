import pytest
from typess.portfolio_breakdown import PortfolioBreakdown


@pytest.fixture(name="sample_data")
def fixture_sample_data():
    return [{"currency": "BTC", "available_balance": "0.5"}, {"currency": "GBP", "available_balance": "1000"}]


@pytest.fixture(name="bitcoin_price")
def fixture_bitcoin_price():
    return 30000


def test_initialization(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    assert pb.portfolio == {"BTC": 0.5, "GBP": 1000}
    assert pb.bitcoin_price == 30000


def test_get_formatted(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    formatted = pb.formatted
    assert "0.5 BTC" in formatted
    assert "1000.0 GBP" in formatted


def test_get_bitcoin_price(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    assert pb.bitcoin_price == 30000


def test_get_btc_percentage(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    btc_percentage = pb.btc_percentage
    expected_percentage = (0.5 * 30000 / (0.5 * 30000 + 1000)) * 100
    assert pytest.approx(btc_percentage, 0.01) == expected_percentage


def test_get_btc_in_gbp(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    btc_in_gbp = pb.btc_in_gbp
    assert btc_in_gbp == 0.5 * 30000


def test_get_total_value_gbp(sample_data, bitcoin_price):
    pb = PortfolioBreakdown(sample_data, bitcoin_price)
    total_value = pb.total_value_gbp
    assert total_value == 0.5 * 30000 + 1000


def test_zero_bitcoin_price(sample_data):
    with pytest.raises(ValueError):
        PortfolioBreakdown(sample_data, 0)


def test_empty_portfolio(bitcoin_price):
    pb = PortfolioBreakdown([], bitcoin_price)
    assert pb.btc_percentage == 0
    assert pb.btc_in_gbp == 0
    assert pb.total_value_gbp == 0
