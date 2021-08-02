import django_filters
from django.contrib.postgres.search import TrigramSimilarity
import re
from django import forms
from .models import ScriptVersion


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
    author = django_filters.filters.CharFilter(
        method="search_authors", label="Author"
    )
    search = django_filters.filters.CharFilter(
        method="search_scripts", label="Search"
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def include_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.filter(content__contains=[{"id": character.lower()}])
        return queryset

    def exclude_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.exclude(content__contains=[{"id": character.lower()}])
        return queryset

    def search_scripts(self, queryset, name, value):
        queryset = annotate_queryset(queryset, 'script__name', value)
        for item in queryset:
            print(f"{item.script.name} {item.similarity}")
        return queryset.filter(similarity__gt=0).order_by('-similarity')

    def search_authors(self, queryset, name, value):
        queryset = annotate_queryset(queryset, 'author', value)
        for item in queryset:
            print(f"{item.author} {item.similarity}")
        return queryset.filter(similarity__gt=0.3).order_by('-similarity')

    class Meta:
        model = ScriptVersion
        fields = [
            "search",
            "script_type",
            "include",
            "exclude",
            "author",
            "all_scripts",
        ]
