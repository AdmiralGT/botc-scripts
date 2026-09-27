import django_filters
from django import forms
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count
from django_filters import rest_framework as filters

from scripts import models, script_json, widgets

edition_choices = (
    (models.Edition.BASE, models.Edition.BASE.label),
    (models.Edition.KICKSTARTER, models.Edition.KICKSTARTER.label),
    (models.Edition.CAROUSEL, models.Edition.CAROUSEL.label),
    (models.Edition.ALL, models.Edition.ALL.label),
)


def include_characters(queryset, value):
    ids = [{"id": character_id} for character_id in script_json.character_ids(value)]
    if not ids:
        return queryset
    return queryset.filter(content__contains=ids)


def exclude_characters(queryset, value):
    for character_id in script_json.character_ids(value):
        queryset = queryset.exclude(content__contains=[{"id": character_id}])
    return queryset


def filter_homebrewiness(queryset, include_hybrid, include_homebrew):
    if not include_hybrid:
        queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HYBRID)
    if not include_homebrew:
        queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HOMEBREW)
    return queryset


def trigram_filter(queryset, field, value, alias, min_similarity=0):
    """
    Annotates the queryset with the trigram similarity of field to value (as alias) and keeps rows above min_similarity.
    """
    queryset = queryset.annotate(**{alias: TrigramSimilarity(field, value)})
    return queryset.filter(**{f"{alias}__gt": min_similarity})


def advanced_search_queryset(data):
    """
    Build the ScriptVersion queryset for the Advanced Search from the cleaned data of an AdvancedSearchForm.

    The result is a lazy queryset with a stable ordering, so it can be paginated by the database.
    """
    if data.get("all_scripts", False):
        queryset = models.ScriptVersion.objects.all()
    else:
        queryset = models.ScriptVersion.objects.filter(latest=True)

    queryset = filter_homebrewiness(queryset, data.get("include_hybrid", False), data.get("include_homebrew", False))

    if data.get("script_type") == models.ScriptTypes.TEENSYVILLE:
        queryset = queryset.exclude(script_type=models.ScriptTypes.FULL)
    else:
        queryset = queryset.exclude(script_type=models.ScriptTypes.TEENSYVILLE)

    if data.get("name"):
        queryset = trigram_filter(queryset, "script__name", data.get("name"), "name_similarity")
    if data.get("author"):
        queryset = trigram_filter(queryset, "author", data.get("author"), "author_similarity")

    if data.get("includes_characters"):
        queryset = include_characters(queryset, data.get("includes_characters"))
    if data.get("excludes_characters"):
        queryset = exclude_characters(queryset, data.get("excludes_characters"))

    queryset = queryset.filter(edition__lte=data.get("edition"))
    tags = data.get("tags")
    if data.get("tag_combinations") == "AND":
        for tag in tags:
            queryset = queryset.filter(tags=tag)
    elif tags:
        queryset = queryset.filter(tags__in=tags)

    for field in ("townsfolk", "outsiders", "minions", "demons", "fabled", "travellers", "loric"):
        values = data.get(f"number_of_{field}")
        if values:
            queryset = queryset.filter(**{f"num_{field}__in": values})

    if data.get("minimum_number_of_likes"):
        queryset = queryset.filter(score__gte=data.get("minimum_number_of_likes"))
    if data.get("minimum_number_of_favourites"):
        queryset = queryset.filter(num_favs__gte=data.get("minimum_number_of_favourites"))
    if data.get("minimum_number_of_comments"):
        queryset = queryset.annotate(num_comments=Count("script__comments", distinct=True))
        queryset = queryset.filter(num_comments__gte=data.get("minimum_number_of_comments"))

    return queryset.order_by("-pk")


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
            return queryset.filter(latest=True)
        return queryset

    def filter_mono_demon_scripts(self, queryset, name, value):
        if value:
            return queryset.filter(num_demons=1)
        return queryset

    def filter_hybrid_scripts(self, queryset, name, value):
        return filter_homebrewiness(queryset, include_hybrid=value, include_homebrew=True)

    def filter_homebrew_scripts(self, queryset, name, value):
        return filter_homebrewiness(queryset, include_hybrid=True, include_homebrew=value)

    def filter_my_scripts(self, queryset, name, value):
        if value:
            return queryset.filter(script__owner=self.request.user)
        return queryset

    def include_characters(self, queryset, name, value):
        return include_characters(queryset, value)

    def exclude_characters(self, queryset, name, value):
        return exclude_characters(queryset, value)

    def _is_explicitly_ordered(self):
        try:
            return "ordering" in self.request.query_params
        except AttributeError:
            return False

    def search_scripts(self, queryset, name, value):
        if self._is_explicitly_ordered():
            return trigram_filter(queryset, "script__name", value, "similarity", min_similarity=0.3)
        return trigram_filter(queryset, "script__name", value, "similarity").order_by("-similarity")

    def search_authors(self, queryset, name, value):
        queryset = trigram_filter(queryset, "author", value, "similarity", min_similarity=0.3)
        if self._is_explicitly_ordered():
            return queryset
        return queryset.order_by("-similarity")


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

    def display_favourites(self, queryset, _, value):
        if value:
            return queryset.filter(script__favourites__user=self.request.user)
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
