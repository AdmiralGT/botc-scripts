import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from scripts import models
from tests.samples import TROUBLE_BREWING

pytestmark = pytest.mark.django_db


def test_anonymous_upload_creates_script(upload):
    response = upload(author="Steven")

    version = models.ScriptVersion.objects.get()
    assert response.status_code == 302
    assert response.url == f"/script/{version.script.pk}"
    assert version.script.name == "Trouble Brewing"
    assert version.script.owner is None
    assert version.author == "Steven"
    assert version.latest
    assert version.edition == models.Edition.BASE
    assert version.homebrewiness == models.Homebrewiness.CLOCKTOWER
    assert (version.num_townsfolk, version.num_outsiders, version.num_minions, version.num_demons) == (13, 4, 4, 1)


def test_authenticated_upload_sets_owner(client, upload, user):
    client.force_login(user)
    upload()

    assert models.Script.objects.get().owner == user


def test_anonymous_flag_leaves_script_unowned(client, upload, user):
    client.force_login(user)
    upload(anonymous=True)

    assert models.Script.objects.get().owner is None


def test_new_version_becomes_latest(client, upload, user):
    client.force_login(user)
    upload(version="1")
    upload(version="2", content=[{"id": "amnesiac"}, *TROUBLE_BREWING[1:]])

    v1, v2 = models.ScriptVersion.objects.get(version="1"), models.ScriptVersion.objects.get(version="2")
    assert not v1.latest
    assert v2.latest
    assert v2.edition == models.Edition.KICKSTARTER


def test_non_owner_cannot_upload_new_version(client, upload, make_script, user, other_user):
    make_script(owner=user)
    client.force_login(other_user)

    response = upload(version="2", content=TROUBLE_BREWING[:-1])

    assert response.status_code == 200
    assert "You are not the owner of this script" in response.content.decode()
    assert models.ScriptVersion.objects.count() == 1


def test_same_version_with_different_content_is_rejected(upload, make_script):
    make_script()

    response = upload(version="1", content=TROUBLE_BREWING[:-1])

    assert response.status_code == 200
    assert "Version 1 already exists" in response.content.decode()
    assert models.ScriptVersion.objects.count() == 1


def test_invalid_json_is_rejected(client):
    response = client.post(
        "/script/upload",
        {
            "name": "Broken",
            "script_type": models.ScriptTypes.FULL,
            "version": "1",
            "content": SimpleUploadedFile("script.json", b"{not json", "application/json"),
        },
    )

    assert response.status_code == 200
    assert not models.Script.objects.exists()
