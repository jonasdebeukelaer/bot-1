import pytest
from src.bot.util import five_sig_fig

def test_valid_input_float():
    input_val = 123.456789
    expected_output = "123.46"
    result = five_sig_fig(input_val)
    assert result == expected_output

def test_nan_input():
    input_val = float("nan")
    expected_output = "nan"
    result = five_sig_fig(input_val)
    assert result == expected_output

def test_valid_input_string():
    input_val = "123.456789"
    expected_output = "123.46"
    result = five_sig_fig(input_val)
    assert result == expected_output

def test_valid_input_integer():
    input_val = 123456
    expected_output = "123460"
    result = five_sig_fig(input_val)
    assert result == expected_output

def test_invalid_input():
    input_val = "not a number"
    expected_output = "not a number"
    result = five_sig_fig(input_val)
    assert result == expected_output

@pytest.mark.parametrize("input_val, expected_output", [
    (0.0001234, "0.0001234"),
    (1234567, "1234600"),
    (-0.0001234, "-0.0001234"),
    (-1234567, "-1234600"),
])
def test_various_inputs(input_val, expected_output):
    result = five_sig_fig(input_val)
    assert result == expected_output