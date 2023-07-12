from django.core.exceptions import ValidationError
from versionfield.forms import VersionField
from scripts import models


def check_for_homebrew(item):
    """
    Homebrew characters are not supported in the custom script database.
    """
    if item.get("id", "") != "_meta":
        if len(item) > 1:
            raise ValidationError(
                f"Only officially supported characters from https://bloodontheclocktower.com/script/ are supported"
            )


def prevent_fishbucket(json):
    """
    Stop people trying to upload Fishbucket scripts, we automatically generate them.
    """
    if len(json) > 50:
        raise ValidationError(
            f'The script database limits scripts to 50 characters. If you\'re trying to upload a "Fishbucket" script,'
            " this is automatically generated at https://botcscripts.com/script/all_roles"
        )


def validate_json(json):
    contains_character = False
    prevent_fishbucket(json)
    for item in json:
        check_for_homebrew(item)
        if not contains_character:
            try:
                models.Character.objects.get(
                    character_id=item.get("id", "DoesNotExist")
                )
                contains_character = True
            except models.Character.DoesNotExist:
                continue
    if not contains_character:
        raise ValidationError(
            f"Scripts must contain at least 1 official Blood on the Clocktower character"
        )
    return


def valid_version(value):
    field = VersionField()
    field.check_format(value)
