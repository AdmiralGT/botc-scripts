"""
Regression tests for the homebrew character takeover bug.

A homebrew character id belongs to the script that introduced it. Uploading a script
that reuses another script's homebrew id used to silently overwrite that character and
reassign it, because the ownership check only ran when the uploaded script name already
existed, and the character-creation code overwrote a foreign-owned character instead of
leaving it alone. An anonymous user could take over any homebrew character by uploading
under a brand new script name.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from requests.exceptions import Timeout

from scripts import models
from scripts.views import create_characters_and_determine_homebrew_status

FOREIGN_HOMEBREW = {
    "id": "customimp",
    "name": "Hacked Imp",
    "team": "demon",
    "ability": "Hacked ability",
}


def _fake_requests_get(url, *args, **kwargs):
    if "roles.json" in url:
        response = MagicMock()
        response.ok = True
        response.content = b"[]"
        return response
    raise Timeout


def _make_victim_character():
    victim = User.objects.create_user("victim")
    victim_script = models.Script.objects.create(name="Victim Script", owner=victim)
    character = models.HomebrewCharacter.objects.create(
        character_id="customimp",
        script=victim_script,
        character_name="Original Imp",
        character_type=models.CharacterType.DEMON,
        ability="Original ability",
    )
    return victim_script, character


@pytest.mark.django_db
@patch("requests.get", side_effect=_fake_requests_get)
def test_upload_cannot_take_over_another_scripts_homebrew(_requests_get, client):
    victim_script, _ = _make_victim_character()

    content = (
        b'[{"id": "washerwoman"}, '
        b'{"id": "customimp", "name": "Hacked Imp", "team": "demon", "ability": "Hacked ability"}]'
    )
    response = client.post(
        reverse("upload"),
        {
            "name": "Attacker Script",
            "author": "Attacker",
            "script_type": models.ScriptTypes.FULL,
            "version": "1",
            "content": SimpleUploadedFile("script.json", content, content_type="application/json"),
        },
    )

    # The upload is rejected, so the form re-renders rather than redirecting.
    assert response.status_code == 200
    assert not models.Script.objects.filter(name="Attacker Script").exists()

    character = models.HomebrewCharacter.objects.get(character_id="customimp")
    assert character.script == victim_script
    assert character.character_name == "Original Imp"
    assert character.ability == "Original ability"


@pytest.mark.django_db
@patch("requests.get", side_effect=_fake_requests_get)
def test_create_characters_does_not_overwrite_foreign_homebrew(_requests_get):
    victim_script, _ = _make_victim_character()
    attacker_script = models.Script.objects.create(name="Attacker Script")

    create_characters_and_determine_homebrew_status([FOREIGN_HOMEBREW], attacker_script)

    character = models.HomebrewCharacter.objects.get(character_id="customimp")
    assert character.script == victim_script
    assert character.character_name == "Original Imp"
    assert character.ability == "Original ability"


@pytest.mark.django_db
@patch("requests.get", side_effect=_fake_requests_get)
def test_create_characters_adopts_orphan_homebrew(_requests_get):
    orphan = models.HomebrewCharacter.objects.create(
        character_id="customimp",
        script=None,
        character_name="Orphan",
        character_type=models.CharacterType.DEMON,
        ability="Orphan ability",
    )
    script = models.Script.objects.create(name="Adopter Script")

    create_characters_and_determine_homebrew_status([FOREIGN_HOMEBREW], script)

    orphan.refresh_from_db()
    assert orphan.script == script
    assert orphan.character_name == "Hacked Imp"
