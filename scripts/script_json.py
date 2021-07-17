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


def validate_json(self, json_data):
    pass
