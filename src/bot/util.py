from functools import singledispatch
from typing import Any


@singledispatch
def five_sig_fig(val: Any) -> str:
    return val


@five_sig_fig.register(float)
@five_sig_fig.register(int)
def _(val: float) -> str:
    return f"{val:.5g}"


@five_sig_fig.register(str)
def _(val: str) -> str:
    if val.replace(".", "", 1).isdigit():
        return f"{float(val):.5g}"
    return val
