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
                "Only officially supported characters from https://bloodontheclocktower.com/script/ are supported"
            )


def prevent_fishbucket(json):
    """
    Stop people trying to upload Fishbucket scripts, we automatically generate them.
    """
    if len(json) > 50:
        raise ValidationError(
            'The script database limits scripts to 50 characters. If you\'re trying to upload a "Fishbucket" script,'
            " this is automatically generated at https://botcscripts.com/script/all_roles"
        )


def validate_json(json):
    if settings.DISABLE_VALIDATORS:
        return

    prevent_fishbucket(json)
    return


def validate_homebrew_character(json, script):
    for item in json:
        if item.get("id", "") == "_meta":
            continue

        try:
            homebrew_character = models.HomebrewCharacter.objects.get(character_id=item.get("id"))
            if homebrew_character.script and homebrew_character.script != script:
                raise ValidationError(
                    f"Character {item.get('id')} is already in the database with a different script ({homebrew_character.script.name}). Please choose another character ID"
                )
        except models.HomebrewCharacter.DoesNotExist:
            pass


def valid_version(value):
    field = VersionField()
    field.check_format(value)
