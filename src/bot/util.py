from functools import singledispatch
from typing import Any


@singledispatch
def five_sig_fig(val: Any) -> str:
    return val


@five_sig_fig.register(float)
@five_sig_fig.register(int)
def _(val: float | int) -> str:
    return _format_float(val)


@five_sig_fig.register(str)
def _(val: str) -> str:
    if val.replace(".", "", 1).isdigit():
        return _format_float(float(val))
    return val


def _format_float(val: float) -> str:
    """
    Format a float to 5 significant figures.
    Ensures the output is not in scientific notation.
    """
    sig_fig = 5
    num = f"{val:.5g}"

    if "e+" in num:
        digits, exponent = num.split("e+")
        digits = digits.replace(".", "")
        zeros = "0" * (int(exponent) - (sig_fig - 1))
        return f"{digits}{zeros}"
    elif "e-" in num:
        digits, exponent = num.split("e-")
        digits = digits.replace(".", "")
        zeros = "0" * (int(exponent) - (sig_fig - 1))
        return f"0.{zeros}{digits}"
    else:
        return num
