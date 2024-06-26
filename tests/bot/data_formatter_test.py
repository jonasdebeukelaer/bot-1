import pytest
from src.bot.data_formatter import DataFormatter


@pytest.fixture(name="taapi_indicators_hourly")
def fixture_taapi_indicators_hourly():
    return [
        {
            "data": [
                {
                    "result": {
                        "volume": 6.7363608699999915,
                        "low": 48093.72,
                        "close": 48208.92,
                        "high": 48408.58,
                        "open": 48273.58,
                        "timestampHuman": "2024-06-26 20:00:00 (Wednesday) UTC",
                        "timestamp": 1719432000,
                    },
                    "id": "candle",
                    "errors": [],
                    "indicator": "candle",
                },
                {"result": {"value": [48208.92]}, "id": "price", "errors": [], "indicator": "price"},
                {"result": {"value": [48623.675183355284]}, "id": "50EMA", "errors": [], "indicator": "ema"},
                {"result": {"value": [40.897358484725075]}, "id": "RSI", "errors": [], "indicator": "rsi"},
                {
                    "result": {
                        "valueMACDHist": [-58.59995092755177],
                        "valueMACD": [-53.22936690697679],
                        "valueMACDSignal": [5.3705840205749755],
                    },
                    "id": "MACD",
                    "errors": [],
                    "indicator": "macd",
                },
            ],
            "id": "2024-06-26 20:00:00 (Wednesday) UTC",
        },
        {
            "data": [
                {"result": {"value": [1111]}, "id": "price", "errors": [], "indicator": "price"},
                {"result": {"value": [1234.22]}, "id": "50EMA", "errors": [], "indicator": "ema"},
            ],
            "id": "2024-06-26 21:00:00 (Wednesday) UTC",
        },
    ]


@pytest.fixture(name="taapi_indicators_daily")
def fixture_taapi_indicators_daily():
    return [
        {
            "data": [{"result": {"value": [40]}, "id": "RSI", "errors": [], "indicator": "rsi"}],
            "id": "2024-06-26 00:00:00 (Wednesday) UTC",
        },
        {
            "data": [{"result": {"value": [1111]}, "id": "price", "errors": [], "indicator": "price"}],
            "id": "2024-06-27 00:00:00 (Thursday) UTC",
        },
        {
            "data": [{"result": {"value": [1111]}, "id": "price", "errors": [], "indicator": "price"}],
            "id": "2024-06-28 00:00:00 (Friday) UTC",
        },
    ]


@pytest.fixture(name="alt_me_data")
def fixture_alt_me_data():
    return [
        {"data": {"timestamp": "26-06-2024", "value_classification": "Fear"}},
        {"data": {"timestamp": "27-06-2024", "value_classification": "Greed"}},
    ]


@pytest.fixture(name="formatter")
def fixture_formatter():
    return DataFormatter()


def test_formats_indicators_correctly_hourly(formatter, taapi_indicators_hourly):
    expected_output = "timestamp: 2024-06-26 20:00:00, day_of_week: Wednesday, candle_volume: 6.7364, candle_high: 48409, candle_low: 48094, candle_open: 48274, candle_close: 48209, price: 48209, 50EMA: 48624, RSI: 40.897, MACD: -53.229, MACD_signal: 5.3706, MACD_hist: -58.6\ntimestamp: 2024-06-26 21:00:00, day_of_week: Wednesday, price: 1111, 50EMA: 1234.2"
    assert formatter.format_hourly_data(taapi_indicators_hourly) == expected_output


def test_formats_indicators_correctly_daily(formatter, taapi_indicators_daily, alt_me_data):
    expected_output = "timestamp: 2024-06-26 00:00:00, day_of_week: Wednesday, RSI: 40, fear_greed_index_class: Fear\ntimestamp: 2024-06-27 00:00:00, day_of_week: Thursday, price: 1111, fear_greed_index_class: Greed\ntimestamp: 2024-06-28 00:00:00, day_of_week: Friday, price: 1111, fear_greed_index_class: Unknown"
    assert formatter.format_daily_data(taapi_indicators_daily, alt_me_data) == expected_output


def test_input_list_is_empty(formatter):
    taapi_indicators = []
    expected_output = "No data available"
    assert formatter.format_hourly_data(taapi_indicators) == expected_output
