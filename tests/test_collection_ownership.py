"""
Tests for collection ownership: only the owner of a collection can edit it or add scripts to it,
others get a 403. Unknown or malformed ids are a 404.

These tests need a PostgreSQL database (see DEVELOPMENT.md).
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from versionfield import Version

from scripts import models


def make_script_version(name="Some Script", version="1.0.0"):
    script = models.Script.objects.create(name=name)
    return models.ScriptVersion.objects.create(
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
    )


@pytest.mark.django_db
def test_owner_can_add_a_script_to_their_own_collection(client):
    owner = User.objects.create_user(username="owner", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")
    script_version = make_script_version()

    client.force_login(owner)
    response = client.post(
        reverse("add_to_collection"),
        {"collection": collection.pk, "script_version": script_version.pk},
    )

    assert response.status_code == 302
    assert list(collection.scripts.all()) == [script_version]


@pytest.mark.django_db
def test_a_different_user_cannot_add_a_script_to_someone_elses_collection(client):
    owner = User.objects.create_user(username="owner", password="password")
    attacker = User.objects.create_user(username="attacker", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")
    script_version = make_script_version()

    client.force_login(attacker)
    response = client.post(
        reverse("add_to_collection"),
        {"collection": collection.pk, "script_version": script_version.pk},
    )

    assert response.status_code == 403
    assert collection.scripts.count() == 0


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    owner = User.objects.create_user(username="owner", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")
    script_version = make_script_version()

    response = client.post(
        reverse("add_to_collection"),
        {"collection": collection.pk, "script_version": script_version.pk},
    )

    assert response.status_code == 302
    assert "login" in response.url
    assert collection.scripts.count() == 0


@pytest.mark.django_db
def test_unknown_collection_is_a_404(client):
    owner = User.objects.create_user(username="owner", password="password")
    script_version = make_script_version()

    client.force_login(owner)
    response = client.post(
        reverse("add_to_collection"),
        {"collection": 999999, "script_version": script_version.pk},
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_script_version_is_a_404(client):
    owner = User.objects.create_user(username="owner", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")

    client.force_login(owner)
    response = client.post(
        reverse("add_to_collection"),
        {"collection": collection.pk, "script_version": 999999},
    )

    assert response.status_code == 404
    assert collection.scripts.count() == 0


@pytest.mark.django_db
def test_malformed_collection_id_is_a_404(client):
    owner = User.objects.create_user(username="owner", password="password")
    script_version = make_script_version()

    client.force_login(owner)
    response = client.post(
        reverse("add_to_collection"),
        {"collection": "abc", "script_version": script_version.pk},
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_can_edit_their_own_collection(client):
    owner = User.objects.create_user(username="owner", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")

    client.force_login(owner)
    assert client.get(f"/collection/{collection.pk}/edit").status_code == 200

    response = client.post(f"/collection/{collection.pk}/edit", {"name": "Renamed", "description": "", "notes": ""})

    assert response.status_code == 302
    collection.refresh_from_db()
    assert collection.name == "Renamed"
    assert collection.owner == owner


@pytest.mark.django_db
def test_a_different_user_cannot_view_the_edit_page(client):
    owner = User.objects.create_user(username="owner", password="password")
    attacker = User.objects.create_user(username="attacker", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")

    client.force_login(attacker)

    assert client.get(f"/collection/{collection.pk}/edit").status_code == 403


@pytest.mark.django_db
def test_a_different_user_cannot_edit_or_take_over_someone_elses_collection(client):
    owner = User.objects.create_user(username="owner", password="password")
    attacker = User.objects.create_user(username="attacker", password="password")
    collection = models.Collection.objects.create(owner=owner, name="My Collection")

    client.force_login(attacker)
    response = client.post(f"/collection/{collection.pk}/edit", {"name": "Hijacked", "description": "", "notes": ""})

    assert response.status_code == 403
    collection.refresh_from_db()
    assert collection.name == "My Collection"
    assert collection.owner == owner
