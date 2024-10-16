import json as js

def get_author_from_json(json):
    return get_metadata_field_from_json(json, "author")


def get_name_from_json(json):
    return get_metadata_field_from_json(json, "name")


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


def strip_special_characters_from_json(json):
    new_json = []
    for item in json:
        if not isinstance(item, dict):
            raise JSONError(f"Unexpected script element: {item}")

        character = item.get("id", "")
        if character == "_meta":
            new_json.append(item)
            continue
        new_json.append({"id": strip_special_characters(character)})

    return new_json


def get_json_content(data):
    json_content = data.get("content", None)
    if not json_content:
        raise JSONError("Could not read file type")
    json = js.loads(json_content.read().decode("utf-8"))
    json_content.seek(0)
    json = revert_to_old_format(json)
    json = strip_special_characters_from_json(json)
    return json