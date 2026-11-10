import pytest
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient

from scripts import models
from tests.samples import TROUBLE_BREWING

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_writer(user):
    user.user_permissions.add(Permission.objects.get(codename="api_write_permission"))
    return user


def test_list_scripts(api_client, make_script):
    make_script(name="First")
    make_script(name="Second")

    response = api_client.get("/api/scripts/")

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert [s["name"] for s in response.data["results"]] == ["Second", "First"]


def test_list_latest_only(api_client, make_script):
    make_script(version="1", latest=False)
    latest = make_script(version="2")

    response = api_client.get("/api/scripts/", {"latest": "true"})

    assert [s["pk"] for s in response.data["results"]] == [latest.pk]


def test_retrieve_script(api_client, make_script):
    version = make_script(author="Steven")

    response = api_client.get(f"/api/scripts/{version.pk}/")

    assert response.status_code == 200
    assert response.data["name"] == "Trouble Brewing"
    assert response.data["author"] == "Steven"
    assert response.data["content"] == TROUBLE_BREWING


def test_retrieve_json(api_client, make_script):
    version = make_script()

    response = api_client.get(f"/api/scripts/{version.pk}/json/")

    assert response.status_code == 200
    assert response.data == TROUBLE_BREWING


def test_anonymous_cannot_create(api_client):
    payload = {"name": "New", "version": "1", "script_type": "Full", "content": TROUBLE_BREWING}

    response = api_client.post("/api/scripts/", payload, format="json")

    assert response.status_code in (401, 403)
    assert not models.Script.objects.exists()


def test_user_without_permission_cannot_create(api_client, user):
    api_client.force_authenticate(user)
    payload = {"name": "New", "version": "1", "script_type": "Full", "content": TROUBLE_BREWING}

    response = api_client.post("/api/scripts/", payload, format="json")

    assert response.status_code == 403
    assert not models.Script.objects.exists()


def test_user_with_permission_can_create(api_client, api_writer):
    api_client.force_authenticate(api_writer)
    payload = {"name": "New", "version": "1", "script_type": "Full", "content": TROUBLE_BREWING}

    response = api_client.post("/api/scripts/", payload, format="json")

    version = models.ScriptVersion.objects.get()
    assert response.status_code == 201
    assert response.data == {"pk": version.pk}
    assert version.script.owner == api_writer
    assert version.num_townsfolk == 13


def test_cannot_create_new_version_of_someone_elses_script(api_client, api_writer, make_script, other_user):
    make_script(name="Owned", owner=other_user)
    api_client.force_authenticate(api_writer)
    payload = {"name": "Owned", "version": "2", "script_type": "Full", "content": TROUBLE_BREWING[:-1]}

    response = api_client.post("/api/scripts/", payload, format="json")

    assert response.status_code == 403
    assert models.ScriptVersion.objects.count() == 1
