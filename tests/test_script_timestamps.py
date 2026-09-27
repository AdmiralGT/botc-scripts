"""
Tests for the uploaded / last updated times shown on the script page (issue #526).

These tests need a PostgreSQL database (see DEVELOPMENT.md).
"""

from datetime import UTC, datetime, timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from versionfield import Version

from scripts import models
from scripts.tables import ClocktowerTable, CollectionClocktowerTable, UserClocktowerTable
from scripts.views import update_script

LONG_AGO = datetime(2024, 1, 2, 12, 0, tzinfo=UTC)
LATER = datetime(2025, 6, 15, 9, 30, tzinfo=UTC)


def make_version(script, version, created=LONG_AGO, updated=None, **kwargs):
    script_version = models.ScriptVersion.objects.create(
        script=script,
        version=Version(version),
        content=[],
        num_townsfolk=13,
        num_outsiders=2,
        num_minions=4,
        num_demons=4,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
        **kwargs,
    )
    # created is auto_now_add, so it can only be set after the fact.
    models.ScriptVersion.objects.filter(pk=script_version.pk).update(created=created, updated=updated or created)
    script_version.refresh_from_db()
    return script_version


@pytest.mark.django_db
def test_new_version_has_updated_time():
    script = models.Script.objects.create(name="Timestamps")
    script_version = models.ScriptVersion.objects.create(
        script=script,
        version=Version("1.0.0"),
        content=[],
        num_townsfolk=13,
        num_outsiders=2,
        num_minions=4,
        num_demons=4,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
    )
    assert script_version.updated is not None
    assert abs(script_version.updated - script_version.created) < timedelta(seconds=5)


@pytest.mark.django_db
def test_last_updated_is_newest_version_update():
    script = models.Script.objects.create(name="Timestamps")
    assert script.last_updated() is None
    make_version(script, "1.0.0", created=LONG_AGO)
    make_version(script, "1.1.0", created=LONG_AGO, updated=LATER)
    make_version(script, "1.2.0", created=LONG_AGO + timedelta(days=1))
    assert script.last_updated() == LATER


@pytest.mark.django_db
def test_update_script_bumps_updated_but_not_created():
    script = models.Script.objects.create(name="Timestamps")
    script_version = make_version(script, "1.0.0")
    cleaned_data = {
        "script_type": models.ScriptTypes.FULL,
        "notes": "New notes",
        "tags": models.ScriptTag.objects.none(),
    }

    update_script(script_version, cleaned_data, "Author", User(is_staff=True))

    script_version.refresh_from_db()
    assert script_version.notes == "New notes"
    assert script_version.created == LONG_AGO
    assert script_version.updated > LONG_AGO + timedelta(days=365)


@pytest.mark.django_db
def test_update_script_with_no_changes_does_not_bump_updated():
    script = models.Script.objects.create(name="Timestamps")
    script_version = make_version(script, "1.0.0", notes="Same notes")
    script_version.tags.set([models.ScriptTag.objects.create(name="Tag", public=True, order=1)])
    cleaned_data = {
        "script_type": script_version.script_type,
        "notes": "Same notes",
        "tags": script_version.tags.all(),
    }

    update_script(script_version, cleaned_data, script_version.author, User(is_staff=True))

    script_version.refresh_from_db()
    assert script_version.updated == LONG_AGO


@pytest.mark.django_db
def test_update_script_blank_author_does_not_bump_updated():
    # The web form gives "" for a blank author, but versions uploaded via the API store None.
    script = models.Script.objects.create(name="Timestamps")
    script_version = make_version(script, "1.0.0", author=None)
    cleaned_data = {"script_type": script_version.script_type, "tags": models.ScriptTag.objects.none()}

    update_script(script_version, cleaned_data, "", User(is_staff=True))

    script_version.refresh_from_db()
    assert script_version.updated == LONG_AGO


@pytest.mark.django_db
def test_update_script_changing_only_tags_bumps_updated():
    script = models.Script.objects.create(name="Timestamps")
    script_version = make_version(script, "1.0.0")
    tag = models.ScriptTag.objects.create(name="Tag", public=True, order=1)
    cleaned_data = {
        "script_type": script_version.script_type,
        "tags": models.ScriptTag.objects.filter(pk=tag.pk),
    }

    update_script(script_version, cleaned_data, script_version.author, User(is_staff=True))

    script_version.refresh_from_db()
    assert script_version.updated > LONG_AGO + timedelta(days=365)


@pytest.mark.django_db
def test_housekeeping_save_does_not_bump_updated():
    script = models.Script.objects.create(name="Timestamps")
    script_version = make_version(script, "1.0.0")

    script_version.latest = False
    script_version.save()

    script_version.refresh_from_db()
    assert script_version.updated == LONG_AGO


@pytest.mark.django_db
def test_script_page_shows_uploaded_and_last_updated(client):
    script = models.Script.objects.create(name="Timestamps")
    make_version(script, "1.0.0", created=LONG_AGO, latest=False)
    make_version(script, "2.0.0", created=LONG_AGO + timedelta(days=30), updated=LATER)

    response = client.get(reverse("script", args=[script.pk, "1.0.0"]))

    assert response.status_code == 200
    content = response.content.decode()
    # Uploaded is for the selected version, last updated is for the whole script.
    assert "Uploaded 2 January 2024" in content
    assert "Last updated 15 June 2025" in content


@pytest.mark.django_db
def test_script_page_hides_last_updated_when_never_edited(client):
    script = models.Script.objects.create(name="Timestamps")
    make_version(script, "1.0.0", created=LONG_AGO)

    response = client.get(reverse("script", args=[script.pk, "1.0.0"]))

    content = response.content.decode()
    assert "Uploaded 2 January 2024" in content
    assert "Last updated" not in content


@pytest.mark.parametrize("table", [ClocktowerTable, UserClocktowerTable, CollectionClocktowerTable])
def test_list_tables_show_updated_but_not_created(table):
    names = [column.name for column in table([]).columns]
    assert "updated" in names
    assert "created" not in names
    assert names.index("updated") < names.index("actions")
