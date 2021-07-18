import django_filters
import re
from django import forms
from .models import ScriptVersion, Script


class ScriptVersionFilter(django_filters.FilterSet):
    all_scripts = django_filters.filters.BooleanFilter(
        method="display_all_scripts", widget=forms.CheckboxInput, label="Display All Versions"
    )
    include = django_filters.filters.CharFilter(method="include_characters", label="Includes characters")
    exclude = django_filters.filters.CharFilter(method="exclude_characters", label="Excludes characters")

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    def include_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.filter(content__contains=[{"id": character}])
        return queryset

    def exclude_characters(self, queryset, name, value):
        for character in re.split(",|;|:|/", value):
            queryset = queryset.exclude(content__contains=[{"id": character}])
        return queryset

    class Meta:
        model = ScriptVersion
        fields = ["type", "all_scripts", "include", "exclude"]
