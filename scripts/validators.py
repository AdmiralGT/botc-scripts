from django.core.exceptions import ValidationError
from versionfield.forms import VersionField


def validate_json(json):
    """
    Homebrew characters are not supported in the custom script database.
    """
    for item in json:
        if item.get("id", "") != "_meta":
            if len(item) > 1:
                raise ValidationError(
                    f"Only officially supported characters from https://bloodontheclocktower.com/script/ are supported"
                )
    return


def valid_version(value):
    field = VersionField()
    field.check_format(value)
