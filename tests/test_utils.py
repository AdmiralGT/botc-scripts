import pytest

from scripts.utils import parse_positive_int


@pytest.mark.parametrize(
    "value, expected",
    [
        ("10", 10),
        ("1", 1),
        ("0", 25),
        ("-3", 25),
        ("abc", 25),
        ("", 25),
        ("2.5", 25),
        (None, 25),
    ],
)
def test_parse_positive_int(value, expected):
    assert parse_positive_int(value, 25) == expected
