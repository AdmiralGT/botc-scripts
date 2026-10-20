import pytest

from scripts import models

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(("action", "model"), [("vote", models.Vote), ("favourite", models.Favourite)])
def test_toggles_for_authenticated_user(client, make_script, user, action, model):
    script = make_script().script
    client.force_login(user)
    url = f"/script/{script.pk}/{action}"

    response = client.post(url, {"next": f"/script/{script.pk}"})
    assert response.status_code == 302
    assert response.url == f"/script/{script.pk}"
    assert model.objects.filter(user=user, parent=script).exists()

    client.post(url)
    assert not model.objects.filter(user=user, parent=script).exists()


@pytest.mark.parametrize(("action", "model"), [("vote", models.Vote), ("favourite", models.Favourite)])
def test_ignored_for_anonymous_user(client, make_script, action, model):
    script = make_script().script

    response = client.post(f"/script/{script.pk}/{action}")

    assert response.status_code == 302
    assert not model.objects.exists()


@pytest.mark.parametrize("action", ["vote", "favourite"])
def test_get_is_404(client, make_script, user, action):
    script = make_script().script
    client.force_login(user)

    assert client.get(f"/script/{script.pk}/{action}").status_code == 404


def test_vote_is_counted_as_score(client, make_script, user, other_user):
    script = make_script().script
    for voter in (user, other_user):
        client.force_login(voter)
        client.post(f"/script/{script.pk}/vote")

    assert models.ScriptVersion.objects.get().score == 2
