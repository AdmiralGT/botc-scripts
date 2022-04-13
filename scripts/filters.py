import re

import django_filters
from django import forms
from django.contrib.postgres.search import TrigramSimilarity

from scripts.models import ScriptVersion, ScriptTag


def annotate_queryset(queryset, field, value):
    return queryset.annotate(similarity=TrigramSimilarity(field, value))


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
        queryset=ScriptTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def include_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/| ", value):
            if character in ",;:/ ":
                continue
            queryset = queryset.filter(content__contains=[{"id": character.lower()}])
        return queryset

    def exclude_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/| ", value):
            if character in ",;:/ ":
                continue
            queryset = queryset.exclude(content__contains=[{"id": character.lower()}])
        return queryset

    def search_scripts(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "script__name", value)
        return queryset.filter(similarity__gt=0).order_by("-similarity")

    def search_authors(self, queryset, name, value):
        queryset = annotate_queryset(queryset, "author", value)
        return queryset.filter(similarity__gt=0.3).order_by("-similarity")

    class Meta:
        model = ScriptVersion
        fields = [
            "search",
            "script_type",
            "include",
            "exclude",
            "author",
            "tags",
            "all_scripts",
        ]
