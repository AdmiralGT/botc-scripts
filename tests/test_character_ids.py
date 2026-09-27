"""
Tests for parsing the character lists typed into the search forms. Pure functions, so no database is needed.
"""

import pytest

from scripts.script_json import character_ids


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Washerwoman", ["washerwoman"]),
        ("Washer woman, Fortune Teller", ["washerwoman", "fortuneteller"]),
        ("Cerenovus; Pit-Hag: Al-Hadikhia / Mezepheles", ["cerenovus", "pithag", "alhadikhia", "mezepheles"]),
        (" , ,; ", []),
        ("", []),
        ("Devil's Advocate", ["devilsadvocate"]),
    ],
)
def test_character_ids(value, expected):
    assert list(character_ids(value)) == expected
