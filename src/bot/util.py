from typing import Any


def format_value(val: Any) -> str:
    """
    formats to 5 significant figures
    """
    if isinstance(val, (float, int)) or (isinstance(val, str) and val.replace(".", "", 1).isdigit()):
        return f"{float(val):.5g}"

    return val
