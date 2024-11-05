import re

import django_filters
from django_filters import rest_framework as filters
from django import forms
from django.contrib.postgres.search import TrigramSimilarity

from scripts import models, widgets, script_json

edition_choices = (
    (models.Edition.BASE, models.Edition.BASE.label),
    (models.Edition.KICKSTARTER, models.Edition.KICKSTARTER.label),
    (models.Edition.UNRELEASED, models.Edition.UNRELEASED.label),
)


def get_characters_by_type(type: models.CharacterType):
    return models.ClocktowerCharacter.objects.filter(character_type=type)


def get_characters_not_in_edition(edition: models.Edition):
    return models.ClocktowerCharacter.objects.filter(edition__gt=edition)


def annotate_queryset(queryset, field, value):
    return queryset.annotate(similarity=TrigramSimilarity(field, value))


def include_characters(queryset, value):
    for character in re.split(",|;|:|/", value):
        character = script_json.strip_special_characters(character.strip())
        if character in ",;:/":
            continue
        queryset = queryset.filter(content__contains=[{"id": name_to_id(character)}])
    return queryset


def exclude_characters(queryset, value):
    for character in re.split(",|;|:|/", value):
        character = script_json.strip_special_characters(character.strip())
        if character in ",;:/":
            continue
        queryset = queryset.exclude(content__contains=[{"id": name_to_id(character)}])
    return queryset


def name_to_id(name: str):
    return name.replace(" ", "_").replace("'", "").lower()


class BaseScriptVersionFilter(filters.FilterSet):
    all_scripts = django_filters.filters.BooleanFilter(
        method="display_all_scripts",
        widget=forms.CheckboxInput,
        label="Display All Versions",
    )
    include = django_filters.filters.CharFilter(method="include_characters", label="Includes characters")
    exclude = django_filters.filters.CharFilter(method="exclude_characters", label="Excludes characters")
    author = django_filters.filters.CharFilter(method="search_authors", label="Author")
    search = django_filters.filters.CharFilter(method="search_scripts", label="Search")
    mono_demon = django_filters.filters.BooleanFilter(
        method="filter_mono_demon_scripts",
        widget=forms.CheckboxInput,
        label="Mono-Demon Scripts Only",
    )
    include_hybrid = django_filters.filters.BooleanFilter(
        method="filter_hybrid_scripts",
        widget=forms.CheckboxInput,
        label="Include Hybrid",
    )
    include_homebrew = django_filters.filters.BooleanFilter(
        method="filter_homebrew_scripts",
        widget=forms.CheckboxInput,
        label="Include Homebrew",
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def filter_mono_demon_scripts(self, queryset, name, value):
        if value:
            return queryset.filter(num_demons=1)
        return queryset

    def filter_hybrid_scripts(self, queryset, name, value):
        if not value:
            return queryset.exclude(homebrewiness=models.Homebrewiness.HYBRID)
        return queryset

    def filter_homebrew_scripts(self, queryset, name, value):
        if not value:
            return queryset.exclude(homebrewiness=models.Homebrewiness.HOMEBREW)
        return queryset

    def filter_my_scripts(self, queryset, name, value):
        if value:
            return queryset.filter(script__owner=self.request.user)
        return queryset

    def include_characters(self, queryset, name, value):
        return include_characters(queryset, value)

    def exclude_characters(self, queryset, name, value):
        return exclude_characters(queryset, value)

    def search_scripts(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "script__name", value)
        try:
            if "ordering" in self.request.query_params.keys():
                return queryset.filter(similarity__gt=0.3)
        except AttributeError:
            pass

        return queryset.filter(similarity__gt=0).order_by("-similarity")

    def search_authors(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "author", value)
        try:
            if "ordering" in self.request.query_params.keys():
                return queryset.filter(similarity__gt=0.3)
        except AttributeError:
            pass

        return queryset.filter(similarity__gt=0.3).order_by("-similarity")


class ScriptVersionFilter(BaseScriptVersionFilter):
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        queryset=models.ScriptTag.objects.all().order_by("order"),
        widget=widgets.BadgePillSelectMultiple,
    )
    edition = django_filters.filters.ChoiceFilter(
        label="Edition",
        method="filter_edition",
        choices=edition_choices,
    )

    def filter_edition(self, queryset, _, value):
        return queryset.filter(edition__lte=value)

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
            "mono_demon",
            "all_scripts",
            "include_hybrid",
            "include_homebrew",
        ]


class FavouriteScriptVersionFilter(ScriptVersionFilter):
    favourites = django_filters.filters.BooleanFilter(
        method="display_favourites", widget=forms.CheckboxInput, label="Favourites"
    )
    my_scripts = django_filters.filters.BooleanFilter(
        method="filter_my_scripts",
        widget=forms.CheckboxInput,
        label="My Scripts",
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
            "mono_demon",
            "favourites",
            "my_scripts",
            "all_scripts",
            "include_hybrid",
            "include_homebrew",
        ]


class CollectionFilter(django_filters.FilterSet, django_filters.filters.QuerySetRequestMixin):
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


class StatisticsFilter(django_filters.FilterSet, django_filters.filters.QuerySetRequestMixin):
    is_owner = django_filters.filters.BooleanFilter(
        widget=forms.CheckboxInput, label="My Scripts only", method="is_owner_function"
    )

    class Meta:
        model = models.ScriptVersion
        fields = [
            "is_owner",
        ]

    def __init__(self, *args, **kwargs):
        super(django_filters.FilterSet, self).__init__(*args, **kwargs)
        if kwargs.get("data") and kwargs.get("data").get("is_owner") == "on":
            self.queryset = models.ScriptVersion.objects.filter(script__owner=self.request.user)

    def is_owner_function(self, queryset, name, value):
        """
        This function exists so that we can use a non-model field. The queryset was already
        altered in the __init__ function.
        """
        return queryset
