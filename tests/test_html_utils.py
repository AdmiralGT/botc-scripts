import pytest
from django.utils.safestring import SafeString

from scripts.html_utils import join_lines_for_html_attribute


def test_lines_are_joined_with_an_encoded_newline():
    result = join_lines_for_html_attribute(["Townsfolk: Chef, Empath", "Demon: Imp"])
    assert result == "Townsfolk: Chef, Empath&#10;Demon: Imp"


def test_result_is_marked_safe():
    assert isinstance(join_lines_for_html_attribute(["Townsfolk: Chef"]), SafeString)


def test_no_lines_gives_an_empty_string():
    assert join_lines_for_html_attribute([]) == ""


def test_ampersands_are_escaped_but_the_separator_is_kept():
    assert join_lines_for_html_attribute(["A & B", "C"]) == "A &amp; B&#10;C"


@pytest.mark.parametrize(
    "payload, forbidden_characters",
    [
        ('"><script>alert(1)</script>', ['"', "<", ">"]),
        ("' onmouseover='alert(1)", ["'"]),
        ("<img src=x onerror=alert(1)>", ["<", ">"]),
    ],
)
def test_user_supplied_text_cannot_break_out_of_the_attribute(payload, forbidden_characters):
    result = join_lines_for_html_attribute([f"Townsfolk: {payload}"])
    for character in forbidden_characters:
        assert character not in result
