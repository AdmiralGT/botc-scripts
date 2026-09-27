"""
Fast unit tests for validate_homebrew_character with the ORM mocked out, so they
run without a database. They cover the ownership guard's branching directly; the
full upload path (form/API wiring and id normalisation) is covered by the DB tests
in test_homebrew_character_takeover.py.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from scripts import models, validators

HOMEBREW = [{"id": "customimp", "name": "Imp", "team": "demon", "ability": "x"}]


def _character(script):
    character = MagicMock()
    character.script = script
    return character


@patch.object(models.HomebrewCharacter.objects, "get")
def test_rejects_character_owned_by_another_script(mock_get):
    mock_get.return_value = _character(script=MagicMock(name="OtherScript"))
    with pytest.raises(ValidationError):
        validators.validate_homebrew_character(HOMEBREW, None)


@patch.object(models.HomebrewCharacter.objects, "get")
def test_allows_same_script(mock_get):
    my_script = MagicMock(name="MyScript")
    mock_get.return_value = _character(script=my_script)
    validators.validate_homebrew_character(HOMEBREW, my_script)


@patch.object(models.HomebrewCharacter.objects, "get")
def test_allows_orphan_character(mock_get):
    mock_get.return_value = _character(script=None)
    validators.validate_homebrew_character(HOMEBREW, MagicMock(name="MyScript"))


@patch.object(models.HomebrewCharacter.objects, "get")
def test_allows_unknown_id(mock_get):
    mock_get.side_effect = models.HomebrewCharacter.DoesNotExist
    validators.validate_homebrew_character(HOMEBREW, None)


@patch.object(models.HomebrewCharacter.objects, "get")
def test_skips_meta_entry(mock_get):
    validators.validate_homebrew_character([{"id": "_meta", "name": "Script"}], None)
    mock_get.assert_not_called()
