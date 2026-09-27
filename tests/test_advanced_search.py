"""
Tests for the Advanced Search results view.

The search criteria live in the query string, so paging and sorting must not depend on any server side state.
These tests need a PostgreSQL database (see DEVELOPMENT.md).
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from versionfield import Version

from scripts import models

RESULTS_URL = "advanced_search_results"


def make_script(index, tags=(), **kwargs):
    script = models.Script.objects.create(name=f"Script {index}")
    version = models.ScriptVersion.objects.create(
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
        **kwargs,
    )
    version.tags.set(tags)
    return version


def result_pks(client, **params):
    response = client.get(reverse(RESULTS_URL), params)
    assert response.status_code == 200
    return response, [row.record.pk for row in response.context["table"].page.object_list]


@pytest.mark.django_db
def test_no_criteria_shows_message_and_empty_table(client):
    make_script(1)
    response, pks = result_pks(client)
    assert pks == []
    assert response.context["search_errors"]


@pytest.mark.django_db
def test_sort_and_page_alone_are_not_criteria(client):
    make_script(1)
    response, pks = result_pks(client, sort="-num_favs", page=1)
    assert pks == []
    assert response.context["search_errors"]


@pytest.mark.django_db
@pytest.mark.parametrize("params", [{"tags": "abc"}, {"minimum_number_of_likes": "many"}, {"edition": "99"}])
def test_invalid_criteria_shows_error_and_empty_table(client, params):
    make_script(1)
    response, pks = result_pks(client, **params)
    assert pks == []
    assert response.context["search_errors"]


@pytest.mark.django_db
def test_old_cache_key_links_show_message(client):
    make_script(1)
    response, pks = result_pks(client, key="0123456789abcdef")
    assert pks == []
    assert response.context["search_errors"]


@pytest.mark.django_db
def test_missing_defaulted_fields_are_filled_in(client):
    """A hand written URL doesn't need script_type, edition or tag_combinations."""
    version = make_script(1)
    response, pks = result_pks(client, all_scripts="on")
    assert pks == [version.pk]
    assert not response.context["search_errors"]


@pytest.mark.django_db
@pytest.mark.parametrize("sort", [None, "-num_favs", "num_favs", "-score", "score", "author", "name", "script_type"])
def test_pagination_has_no_duplicates_or_gaps(client, sort):
    """
    Every script has the same likes, favourites and author, so sorting on them has to fall back to a tiebreaker or
    the same script can appear on more than one page (issue #482).
    """
    expected = {make_script(i).pk for i in range(45)}

    seen = []
    for page in (1, 2, 3):
        params = {"all_scripts": "on", "page": page}
        if sort:
            params["sort"] = sort
        _, pks = result_pks(client, **params)
        seen.extend(pks)

    assert len(seen) == len(set(seen)) == 45
    assert set(seen) == expected


@pytest.mark.django_db
def test_criteria_are_applied_on_every_page(client):
    """Regression test for issue #688: page 2 must still be filtered by the search."""
    tag = models.ScriptTag.objects.create(name="Tagged", order=1)
    tagged = {make_script(i, tags=[tag]).pk for i in range(25)}
    for i in range(25, 50):
        make_script(i)

    seen = []
    for page in (1, 2):
        _, pks = result_pks(client, all_scripts="on", tags=str(tag.pk), page=page)
        seen.extend(pks)

    assert set(seen) == tagged
    assert len(seen) == 25


@pytest.mark.django_db
def test_minimum_likes_is_not_inflated_by_tag_joins(client):
    """One like on a script with two tags must not count as two likes when both tags are required."""
    tags = [models.ScriptTag.objects.create(name=f"Tag {i}", order=i) for i in range(2)]
    version = make_script(1, tags=tags)
    user = User.objects.create_user("voter")
    models.Vote.objects.create(parent=version.script, user=user)

    params = {"all_scripts": "on", "tag_combinations": "AND", "tags": [str(t.pk) for t in tags]}
    _, pks = result_pks(client, minimum_number_of_likes=1, **params)
    assert pks == [version.pk]
    _, pks = result_pks(client, minimum_number_of_likes=2, **params)
    assert pks == []


@pytest.mark.django_db
def test_search_form_page_posts_to_itself(client):
    response = client.get(reverse("advanced_search"))
    assert response.status_code == 200
    assert 'method="post"' in response.content.decode()


@pytest.mark.django_db
def test_valid_post_redirects_to_results_with_criteria_in_url(client):
    tags = [models.ScriptTag.objects.create(name=f"Tag {i}", order=i) for i in range(2)]
    response = client.post(
        reverse("advanced_search"),
        {"script_type": "Full", "edition": "3", "tag_combinations": "AND", "tags": [t.pk for t in tags], "author": ""},
    )
    assert response.status_code == 302
    url = response["Location"]
    assert url.startswith(reverse(RESULTS_URL) + "?")
    assert "csrfmiddlewaretoken" not in url
    assert url.count("tags=") == 2


@pytest.mark.django_db
def test_posted_search_can_be_paged_from_the_redirect_url(client):
    """The whole flow: POST the form, follow the redirect, then page on with the same query string."""
    tag = models.ScriptTag.objects.create(name="Tagged", order=1)
    tagged = {make_script(i, tags=[tag]).pk for i in range(25)}
    for i in range(25, 50):
        make_script(i)

    response = client.post(
        reverse("advanced_search"),
        {
            "script_type": "Full",
            "edition": "3",
            "tag_combinations": "AND",
            "all_scripts": "on",
            "tags": [tag.pk],
        },
    )
    seen = []
    for page in (1, 2):
        page_response = client.get(response["Location"] + f"&page={page}")
        assert page_response.status_code == 200
        seen.extend(row.record.pk for row in page_response.context["table"].page.object_list)

    assert set(seen) == tagged
    assert len(seen) == 25


@pytest.mark.django_db
def test_invalid_post_shows_form_errors_without_redirecting(client):
    response = client.post(reverse("advanced_search"), {"script_type": "Full", "minimum_number_of_likes": "many"})
    assert response.status_code == 200
    assert response.context["form"].errors
