"""
Regression tests for issue #503: two near-simultaneous uploads (or an upload racing a
delete) for the same script used to both pass the "does this version exist" check before
either committed, so both created a version row - sometimes with the same version number,
both marked latest, both showing up in search. Nothing serialized concurrent writes to the
same Script.

The fix locks the Script row (SELECT ... FOR UPDATE, inside an atomic transaction) at the
start of the web upload/delete views and the equivalent API actions, so a second request
for the same script blocks until the first one commits and then sees its result rather than
racing it.

These tests need a real, uncontended database connection per thread, so they use
transaction=True rather than the default django_db (which wraps each test in a rolled back
outer transaction and would not exercise real row locking across threads).
"""

import threading
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from requests.exceptions import Timeout
from versionfield import Version

from scripts import models

SCRIPT_CONTENT = b'[{"id": "washerwoman"}, {"id": "chef"}, {"id": "imp"}]'


def make_version(script, version, latest=True):
    return models.ScriptVersion.objects.create(
        script=script,
        version=Version(version),
        content=[],
        latest=latest,
        num_townsfolk=0,
        num_outsiders=0,
        num_minions=0,
        num_demons=0,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
    )


def upload(client, *, name, version, content=SCRIPT_CONTENT):
    return client.post(
        reverse("upload"),
        {
            "name": name,
            "author": "Race Tester",
            "script_type": models.ScriptTypes.FULL,
            "version": version,
            "content": SimpleUploadedFile("script.json", content, content_type="application/json"),
        },
    )


# ScriptForm.clean() fetches the official schema over the network, and the upload view
# separately fetches the current script tool roles to decide whether an unknown id is a
# brand new official character. Neither should make a real network call in a test, and
# letting either time out for real would make a concurrency test slow and flaky.
#
# scripts/forms.py and scripts/views.py both just `import requests`, so
# "scripts.forms.requests.get" and "scripts.views.requests.get" are two names for the exact
# same requests.get function - patching them separately makes the second patch silently
# clobber the first instead of the two coexisting. Patch requests.get once instead, and
# branch on the URL.
def _fake_requests_get(url, *args, **kwargs):
    if "roles.json" in url:
        response = MagicMock()
        response.ok = True
        response.content = b"[]"
        return response
    # The schema fetch in ScriptForm.clean() treats a timeout as "skip full-schema
    # validation", which is what we want here rather than a real network call.
    raise Timeout


@pytest.mark.django_db(transaction=True)
@patch("requests.get", side_effect=_fake_requests_get)
def test_uploading_the_same_new_version_concurrently_does_not_create_a_duplicate(_requests_get):
    script = models.Script.objects.create(name="Race Script")
    make_version(script, "1.0.0")

    barrier = threading.Barrier(2)
    results = []
    errors = []

    def do_upload():
        try:
            barrier.wait(timeout=5)
            response = upload(Client(), name="Race Script", version="2.0.0")
            results.append(response.status_code)
        except Exception as e:  # noqa: BLE001 - surface any failure from the background thread to the main thread
            errors.append(e)

    threads = [threading.Thread(target=do_upload) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors, errors
    assert results == [302, 302]

    new_versions = models.ScriptVersion.objects.filter(script=script, version=Version("2.0.0"))
    assert new_versions.count() == 1
    assert models.ScriptVersion.objects.filter(script=script, latest=True).count() == 1


@pytest.mark.django_db(transaction=True)
@patch("requests.get", side_effect=_fake_requests_get)
def test_deleting_and_reuploading_the_same_version_concurrently_does_not_duplicate_it(_requests_get):
    # Deleting is owner-only, and re-uploading a version of an already-owned script must be
    # done as that same owner, so both requests are authenticated as the script's owner.
    owner = User.objects.create_user(username="owner", password="password")
    script = models.Script.objects.create(name="Race Script Two", owner=owner)
    make_version(script, "1.0.0")
    v2 = make_version(script, "2.0.0")

    barrier = threading.Barrier(2)
    results = []
    errors = []

    def do_delete():
        try:
            client = Client()
            client.force_login(owner)
            barrier.wait(timeout=5)
            response = client.post(reverse("delete_script", kwargs={"pk": script.pk, "version": str(v2.version)}))
            results.append(("delete", response.status_code))
        except Exception as e:  # noqa: BLE001 - surface any failure from the background thread to the main thread
            errors.append(e)

    def do_reupload():
        try:
            client = Client()
            client.force_login(owner)
            barrier.wait(timeout=5)
            response = upload(client, name="Race Script Two", version="2.0.0")
            results.append(("upload", response.status_code))
        except Exception as e:  # noqa: BLE001 - surface any failure from the background thread to the main thread
            errors.append(e)

    threads = [threading.Thread(target=do_delete), threading.Thread(target=do_reupload)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors, errors
    assert len(results) == 2

    versions = models.ScriptVersion.objects.filter(script=script, version=Version("2.0.0"))
    # Either the delete won the race and the re-upload recreated the version, or the
    # re-upload happened first and the delete then removed it - either is a valid outcome
    # of two real, unordered concurrent requests. What must never happen is two rows for
    # the same version, or more than one version left flagged latest.
    assert versions.count() <= 1
    assert models.ScriptVersion.objects.filter(script=script, latest=True).count() <= 1
