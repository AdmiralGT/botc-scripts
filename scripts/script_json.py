import base64 as b64
import gzip
import json as js
from urllib.parse import quote

from django.core.files.base import File

from scripts import constants

META_ID = "_meta"

_UNKNOWN_ABILITY = "UNKNOWN_ABILITY"


class JSONError(Exception):
    pass


def get_author_from_json(json):
    return get_metadata_field_from_json(json, "author")


def get_name_from_json(json):
    return get_metadata_field_from_json(json, "name")


def get_bootlegger_rules_from_json(json):
    return get_metadata_field_from_json(json, "bootlegger")


def get_metadata_field_from_json(json, field):
    """
    Returns a chosen field from the _meta JSON data.
    """
    for item in json:
        if item.get("id", "") == META_ID:
            return item.get(field, None)
    return None


def revert_to_old_format(json):
    """
    Convert the "list of ID strings" script format into a list of {"id": ...} objects.
    """
    return [{"id": item} if isinstance(item, str) else item for item in json]


def strip_special_characters(character_id):
    return character_id.replace("_", "").replace("-", "").lower()


def name_to_id(name):
    return name.replace(" ", "").replace("'", "").lower()


def strip_special_characters_from_json(json):
    new_json = []
    for item in json:
        if not isinstance(item, dict):
            raise JSONError(f"Unexpected script element: {item}")

        character = item.get("id", "")
        if character != META_ID:
            item["id"] = strip_special_characters(character)
        new_json.append(item)

    return new_json


def _parse_json(raw):
    try:
        return js.loads(raw)
    except js.JSONDecodeError as e:
        raise JSONError(f"Invalid JSON content: {e}") from e


def get_json_content(data):
    json_content = data.get("content", None)
    if not json_content:
        raise JSONError("Could not read file type")

    if isinstance(json_content, File):
        json = _parse_json(json_content.read().decode("utf-8"))
        json_content.seek(0)
    elif isinstance(json_content, (str, bytes, bytearray)):
        json = _parse_json(json_content)
    else:
        json = json_content

    return strip_special_characters_from_json(revert_to_old_format(json))


def _character_ids(json):
    """
    The IDs of every character in a script, in order, ignoring the _meta entry.
    """
    ids = (item.get("id", "") for item in json)
    return [character_id for character_id in ids if character_id != META_ID]


def get_json_additions(old_json, new_json):
    """
    Determine the characters that are in the new JSON but not in the old JSON.

    This is imperfect because a change from an official to a homebrew character of the same name
    is not detected, but we only have the JSON to work from and official characters have limited
    information in the JSON.

    Neither input is modified.
    """
    old_ids = set(_character_ids(old_json))
    return [item for item in new_json if item.get("id", "") not in old_ids and item.get("id", "") != META_ID]


def get_json_changes(old_json, new_json):
    """
    Determine changes to character abilities where the character ID is unchanged.
    """
    new_abilities = {
        item.get("id"): item.get("ability", _UNKNOWN_ABILITY) for item in new_json if item.get("id") != META_ID
    }
    return [
        {"id": item.get("id")}
        for item in old_json
        if item.get("id") != META_ID
        and item.get("id") in new_abilities
        and item.get("ability", _UNKNOWN_ABILITY) != new_abilities[item.get("id")]
    ]


def get_similarity(json1: list, json2: list, same_type: bool) -> int:
    """
    How similar two scripts are, as a percentage of the characters in ``json1`` that are also in ``json2``.

    Scripts of the same type are compared against the larger script, otherwise against the smaller one
    (but never less than a standard Teensyville script) so a Teensyville script isn't considered
    dissimilar to a full script that contains all of its characters.
    """
    ids1 = _character_ids(json1)
    ids2 = _character_ids(json2)
    ids2_set = set(ids2)

    shared = sum(1 for character_id in ids1 if character_id in ids2_set)

    if same_type:
        comparison_size = max(len(ids1), len(ids2))
    else:
        comparison_size = max(min(len(ids1), len(ids2)), constants.STANDARD_TEENSYVILLE_CHARACTER_COUNT)

    if comparison_size == 0:
        return 0
    return round(shared / comparison_size * 100)


def compress_json(json_data):
    json_string = js.dumps(json_data)
    compressed = gzip.compress(json_string.encode("utf-8"))
    base64_encoded = b64.b64encode(compressed).decode("utf-8")
    return quote(base64_encoded)
