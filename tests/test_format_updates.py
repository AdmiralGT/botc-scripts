import pytest
from scripts.script_json import strip_special_characters, strip_special_characters_from_json, revert_to_old_format

@pytest.mark.parametrize("input, expected_output",[
    ("snakecharmer", "snakecharmer"),
    ("pit-hag", "pithag"),
    ("fortune_teller", "fortuneteller"),
    ("Ojo", "ojo"),
    ])
def test_strip_special_characters(input, expected_output):
    output = strip_special_characters(input)
    assert(output == expected_output)


def test_revert_to_old_format():
    json = [
        {
            "id": "_meta",
            "author": "AdmiralGT",
            "name": "Script Name",
        },
        "snakecharmer",
        "fortune_teller",
        "pit-hag",
        "Ojo",
    ]
    expected_json = [
        {
            "id": "_meta",
            "author": "AdmiralGT",
            "name": "Script Name",
        },
        {
            "id": "snakecharmer",
        },
        {
            "id": "fortune_teller",
        },
        {
            "id": "pit-hag",
        },
        {
            "id": "Ojo",
        }
    ]
    json = revert_to_old_format(json)
    assert json == expected_json


def test_strip_special_characters_from_json():
    json = [
        {
            "id": "_meta",
            "author": "AdmiralGT",
            "name": "Script Name",
        },
        {
            "id": "snakecharmer",
        },
        {
            "id": "fortune_teller",
        },
        {
            "id": "pit-hag",
        },
        {
            "id": "Ojo",
        }
    ]
    expected_json = [
        {
            "id": "_meta",
            "author": "AdmiralGT",
            "name": "Script Name",
        },
        {
            "id": "snakecharmer",
        },
        {
            "id": "fortuneteller",
        },
        {
            "id": "pithag",
        },
        {
            "id": "ojo",
        },
    ]

    json = strip_special_characters_from_json(json)
    assert json == expected_json
