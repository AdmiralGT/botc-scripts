import re

import django_filters
from django import forms
from django.contrib.postgres.search import TrigramSimilarity

from scripts import models, characters

edition_choices = (
    (models.Edition.BASE, models.Edition.BASE.label),
    (models.Edition.KICKSTARTER, models.Edition.KICKSTARTER.label),
    (models.Edition.UNRELEASED, models.Edition.UNRELEASED.label),
)


def filter_by_edition(queryset, value):
    edition = models.Edition(int(value))
    for character in characters.get_characters_not_in_edition(edition):
        queryset = queryset.exclude(content__contains=[{"id": character.json_id}])
    return queryset


def annotate_queryset(queryset, field, value):
    return queryset.annotate(similarity=TrigramSimilarity(field, value))


def include_characters(queryset, value):
    for character in re.split(",|;|:|/| ", value):
        if character in ",;:/ ":
            continue
        queryset = queryset.filter(content__contains=[{"id": character.lower()}])
    return queryset


def exclude_characters(queryset, value):
    for character in re.split(",|;|:|/| ", value):
        if character in ",;:/ ":
            continue
        queryset = queryset.exclude(content__contains=[{"id": character.lower()}])
    return queryset


class ScriptVersionFilter(django_filters.FilterSet):
    all_scripts = django_filters.filters.BooleanFilter(
        method="display_all_scripts",
        widget=forms.CheckboxInput,
        label="Display All Versions",
    )
    include = django_filters.filters.CharFilter(
        method="include_characters", label="Includes characters"
    )
    exclude = django_filters.filters.CharFilter(
        method="exclude_characters", label="Excludes characters"
    )
    author = django_filters.filters.CharFilter(method="search_authors", label="Author")
    search = django_filters.filters.CharFilter(method="search_scripts", label="Search")
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        queryset=models.ScriptTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    edition = django_filters.filters.ChoiceFilter(
        field_name=None,
        method="filter_edition",
        choices=edition_choices,
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def include_characters(self, queryset, name, value):
        return include_characters(queryset, value)

    def exclude_characters(self, queryset, name, value):
        return exclude_characters(queryset, value)

    def search_scripts(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "script__name", value)
        return queryset.filter(similarity__gt=0).order_by("-similarity")

    def search_authors(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "author", value)
        return queryset.filter(similarity__gt=0.3).order_by("-similarity")

    def filter_edition(self, queryset, name, value):
        return filter_by_edition(queryset, value)

    class Meta:
        model = models.ScriptVersion
        fields = [
            "search",
            "script_type",
            "include",
            "exclude",
            "edition",
            "author",
            "tags",
            "all_scripts",
        ]


class FavouriteScriptVersionFilter(ScriptVersionFilter):
    favourites = django_filters.filters.BooleanFilter(
        method="display_favourites", widget=forms.CheckboxInput, label="Favourites"
    )

    def display_favourites(self, queryset, name, value):
        if value:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    class Meta:
        model = models.ScriptVersion
        fields = [
            "search",
            "script_type",
            "include",
            "exclude",
            "edition",
            "author",
            "tags",
            "all_scripts",
            "favourites",
        ]


class CollectionFilter(
    django_filters.FilterSet, django_filters.filters.QuerySetRequestMixin
):
    is_owner = django_filters.filters.BooleanFilter(
        widget=forms.CheckboxInput, label="My Collections", method="is_owner_function"
    )

    class Meta:
        model = models.Collection
        fields = [
            "is_owner",
        ]

    def __init__(self, *args, **kwargs):
        super(django_filters.FilterSet, self).__init__(*args, **kwargs)
        if kwargs.get("data") and kwargs.get("data").get("is_owner") == "on":
            self.queryset = models.Collection.objects.filter(owner=self.request.user)

    def is_owner_function(self, queryset, name, value):
        """
        This function exists so that we can use a non-model field. The queryset was already
        altered in the __init__ function.
        """
        return queryset
