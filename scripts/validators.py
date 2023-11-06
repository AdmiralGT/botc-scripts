from django.core.exceptions import ValidationError
from django.conf import settings
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
    if settings.DISABLE_VALIDATORS:
        return

    for item in json:
        # If it's just a string, this is the new TPI format.
        if isinstance(item, str):
            # In which case, we want to turn it into a JSON object.

    MIN_KNOWN_CHARACTERS = round(len(json) / 2)
    contains_character = 0
    prevent_fishbucket(json)
    for item in json:
        check_for_homebrew(item)
        if contains_character < MIN_KNOWN_CHARACTERS:
            try:
                models.Character.objects.get(
                    character_id=item.get("id", "DoesNotExist")
                )
                contains_character += 1
            except models.Character.DoesNotExist:
                continue
    if contains_character < MIN_KNOWN_CHARACTERS:
        raise ValidationError(
            f"Script must contain at least {MIN_KNOWN_CHARACTERS} official Blood on the Clocktower character"
        )
    return


def valid_version(value):
    field = VersionField()
    field.check_format(value)
