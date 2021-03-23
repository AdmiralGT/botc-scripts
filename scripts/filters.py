import django_filters
from django import forms
from .models import ScriptVersion, Script


class ScriptVersionFilter(django_filters.FilterSet):
    latest = django_filters.filters.BooleanFilter(
        method="display_latest", widget=forms.CheckboxInput, initial=True
    )

    def display_latest(self, queryset, name, value):
        if value:
            return queryset.filter(latest=value)
        return queryset

    class Meta:
        model = ScriptVersion
        fields = ["type", "latest"]
