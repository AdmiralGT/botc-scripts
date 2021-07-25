import django_filters
import re
from django import forms
from .models import ScriptVersion


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
        field_name="author", lookup_expr="icontains"
    )
    search = django_filters.filters.CharFilter(
        field_name="script__name", lookup_expr="icontains", label="Search"
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def include_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.filter(content__icontains=[{"id": character}])
        return queryset

    def exclude_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.exclude(content__icontains=[{"id": character}])
        return queryset

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
