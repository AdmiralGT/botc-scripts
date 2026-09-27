import json

import pytest

from scripts import models
from tests.samples import TROUBLE_BREWING

pytestmark = pytest.mark.django_db


def test_script_list_shows_latest_versions(client, make_script):
    make_script(name="Old Script", version="1", latest=False)
    make_script(name="Current Script", version="1")

    response = client.get("/")

    assert response.status_code == 200
    assert "Current Script" in response.content.decode()
    assert "Old Script" not in response.content.decode()


def test_script_page_renders(client, make_script):
    version = make_script(notes="Some **notes**")

    response = client.get(f"/script/{version.script.pk}")

    assert response.status_code == 200
    assert response.context["script_version"] == version
    assert "Trouble Brewing" in response.content.decode()


def test_script_page_shows_changes_between_versions(client, make_script):
    make_script(version="1")
    latest = make_script(version="2", content=[{"id": "amnesiac"}, *TROUBLE_BREWING[1:]])

    response = client.get(f"/script/{latest.script.pk}")

    changes = {str(version): diff for version, diff in response.context["changes"].items()}
    assert changes["2.0.0"]["additions"] == [{"id": "amnesiac"}]
    assert changes["2.0.0"]["deletions"] == [{"id": "washerwoman"}]


def test_unknown_script_is_404(client):
    assert client.get("/script/999999").status_code == 404


def test_download_json_returns_content_and_counts_downloads(client, make_script):
    version = make_script()

    response = client.get(f"/script/{version.script.pk}/{version.version}/download")

    assert response.status_code == 200
    assert response["Content-Disposition"] == 'attachment; filename="Trouble Brewing_1_0_0.json"'
    assert json.loads(b"".join(response.streaming_content)) == version.content
    assert models.Script.objects.get().num_downloads == 1
