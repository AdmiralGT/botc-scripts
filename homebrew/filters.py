import django_filters
from django import forms
from scripts import filters, models

class HomebrewVersionFilter(filters.BaseScriptVersionFilter):
    class Meta:
        model = models.ScriptVersion
        fields = [
            "search",
            "script_type",
            "include",
            "exclude",
            # "homebrewiness",
            "author",
            "mono_demon",
            "all_scripts",
        ]


class FavouriteHomebrewVersionFilter(HomebrewVersionFilter):
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
            # "homebrewiness",
            "author",
            "mono_demon",
            "favourites",
            "my_scripts",
            "all_scripts",
        ]


