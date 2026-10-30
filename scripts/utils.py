def parse_positive_int(value: str | None, default: int) -> int:
    """
    Parse a user supplied query-string value as an integer >= 1, falling back to ``default``
    when it is missing, not a number, or less than one.
    """
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number >= 1 else default
