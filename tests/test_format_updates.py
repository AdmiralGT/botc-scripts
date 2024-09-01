from scripts.script_json import strip_special_characters_from_json, revert_to_old_format


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
    ]

    json = strip_special_characters_from_json(json)
    assert json == expected_json
