import pytest

from scripts import models
from tests.samples import TROUBLE_BREWING

pytestmark = pytest.mark.django_db


@pytest.fixture
def search(client):
    def _search(**criteria):
        data = {"script_type": models.ScriptTypes.FULL, "edition": models.Edition.ALL, "tag_combinations": "AND"}
        response = client.post("/script/search", {**data, **criteria}, follow=True)
        assert response.status_code == 200
        return [row.record for row in response.context["table"].rows]

    return _search


def test_search_by_name_uses_trigram_similarity(search, make_script):
    match = make_script(name="Trouble Brewing")
    make_script(name="Sects and Violets")

    assert search(name="Trouble Brew") == [match]


def test_search_by_included_character(search, make_script):
    make_script(name="Trouble Brewing")
    with_amnesiac = make_script(name="Amnesia", content=[{"id": "amnesiac"}, *TROUBLE_BREWING[1:]])

    assert search(includes_characters="amnesiac") == [with_amnesiac]


def test_search_excludes_older_versions_by_default(search, make_script):
    make_script(version="1", latest=False)
    latest = make_script(version="2")

    assert search() == [latest]
