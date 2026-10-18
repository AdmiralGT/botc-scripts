import base64 as b64
import gzip
import json as js
from urllib.parse import quote

from django.core.files.base import File


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
        if item.get("id", "") == "_meta":
            return item.get(field, None)
    return None


def revert_to_old_format(json):
    old_format_json = []

    for item in json:
        if isinstance(item, str):
            old_format_json.append({"id": item})
        else:
            old_format_json.append(item)

    return old_format_json


class JSONError(Exception):
    pass


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
        if character == "_meta":
            new_json.append(item)
            continue
        item["id"] = strip_special_characters(character)
        new_json.append(item)

    return new_json


def get_json_content(data):
    json_content = data.get("content", None)
    if not json_content:
        raise JSONError("Could not read file type")
    if isinstance(json_content, File):
        try:
            json = js.loads(json_content.read().decode("utf-8"))
        except js.JSONDecodeError as e:
            raise JSONError(f"Invalid JSON content: {e}")
        json_content.seek(0)
    elif isinstance(json_content, (str, bytes, bytearray)):
        try:
            json = js.loads(json_content)
        except js.JSONDecodeError as e:
            raise JSONError(f"Invalid JSON content: {e}")
    else:
        json = json_content
    json = revert_to_old_format(json)
    json = strip_special_characters_from_json(json)
    return json


# Determine the characters that are in the new JSON but not in the old JSON
# This
def get_json_additions(old_json, new_json):
    for old_id in old_json:
        if old_id["id"] == "_meta":
            continue
        for new_id in new_json:
            if new_id["id"] == "_meta":
                continue

            # Check if the IDs are unchanged.
            # This is imperfect because this will detect a change from an Official
            # to a Homebrew character of the same name, but we only have the JSON to do this check
            # and official characters have limited information in the JSON.
            if old_id["id"] == new_id["id"]:
                new_json.remove(new_id)
                continue

    for new_id in new_json:
        if new_id["id"] == "_meta":
            new_json.remove(new_id)
            break

    return new_json


# Determine changes to character abilities where the character ID is unchanged
def get_json_changes(old_json, new_json):
    changed_json = []
    for old_id in old_json:
        if old_id["id"] == "_meta":
            continue
        for new_id in new_json:
            if new_id["id"] == "_meta":
                continue

            ability_changed = old_id.get("ability", "UNKNOWN_ABILITY") != new_id.get("ability", "UNKNOWN_ABILITY")
            if old_id["id"] == new_id["id"] and ability_changed:
                changed_json.append({"id": new_id["id"]})
                continue

    return changed_json


def compress_json(json_data):
    json_string = js.dumps(json_data)
    compressed = gzip.compress(json_string.encode("utf-8"))
    base64_encoded = b64.b64encode(compressed).decode("utf-8")
    return quote(base64_encoded)
