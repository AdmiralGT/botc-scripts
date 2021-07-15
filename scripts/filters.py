import django_filters
from django import forms
from .models import ScriptVersion, Script


class ScriptVersionFilter(django_filters.FilterSet):
    all_scripts = django_filters.filters.BooleanFilter(
        method="display_all_scripts", widget=forms.CheckboxInput, label="Display All"
    )

    def display_all_scripts(self, queryset, name, value):
        if not value:
            return queryset.filter(latest=(not value))
        return queryset

    class Meta:
        model = ScriptVersion
        fields = ["type", "all_scripts"]
