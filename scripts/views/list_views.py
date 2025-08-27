"""
List and search views.
"""
import logging
from typing import Dict, Any, List

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, Case, When, Prefetch, QuerySet
from django.shortcuts import redirect
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, SingleTableView

from scripts import models, filters, tables, forms
from scripts.validators_enhanced import validate_session_ids

logger = logging.getLogger(__name__)


class ScriptsListView(SingleTableMixin, FilterView):
    """Main script list view."""
    
    model = models.ScriptVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_queryset(self) -> QuerySet:
        """Get optimized queryset with prefetch."""
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "tags",
                    queryset=models.ScriptTag.objects.all().order_by("order"),
                )
            )
        )

    def get_filterset_class(self):
        """Get appropriate filter class based on authentication."""
        if self.request.user.is_authenticated:
            return filters.FavouriteScriptVersionFilter
        return filters.ScriptVersionFilter

    def get_filterset_kwargs(self, filterset_class) -> Dict[str, Any]:
        """Set default filter to latest scripts."""
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs

    def get_table_class(self):
        """Get appropriate table class based on authentication."""
        if self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable


class UserScriptsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """List view for user-specific scripts."""
    
    model = models.ScriptVersion
    table_class = tables.UserClocktowerTable
    template_name = "scriptlist.html"
    script_view = None
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]

    def get_filterset_class(self):
        """Get filter class for user scripts."""
        return filters.ScriptVersionFilter

    def get_queryset(self) -> QuerySet:
        """Filter queryset based on script_view type."""
        queryset = super().get_queryset()
        
        if self.script_view == "favourite":
            queryset = queryset.filter(script__favourites__user=self.request.user)
        elif self.script_view == "owned":
            queryset = queryset.filter(script__owner=self.request.user)
            
        return queryset

    def get_filterset_kwargs(self, filterset_class) -> Dict[str, Any]:
        """Set default filter to latest scripts."""
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"latest": True}
        return kwargs


class AdvancedSearchView(generic.FormView):
    """Advanced search form view."""
    
    template_name = "advanced_search.html"
    form_class = forms.AdvancedSearchForm
    
    # Character count ranges (avoid slow dynamic calculation)
    CHARACTER_COUNT_RANGE = range(26)  # 0-25

    def get_form(self):
        """Create form with character count choices."""
        choice_list = [(i, i) for i in self.CHARACTER_COUNT_RANGE]
        
        return forms.AdvancedSearchForm(
            townsfolk_choices=choice_list,
            outsider_choices=choice_list,
            minion_choices=choice_list,
            demon_choices=choice_list,
            fabled_choices=choice_list,
            traveller_choices=choice_list,
            **self.get_form_kwargs(),
        )

    def form_valid(self, form):
        """Process advanced search form."""
        cleaned_data = form.cleaned_data
        
        # Build initial queryset
        if cleaned_data.get("all_scripts"):
            queryset = models.ScriptVersion.objects.all()
        else:
            queryset = models.ScriptVersion.objects.filter(latest=True)
            
        # Apply homebrewiness filters
        queryset = self._apply_homebrewiness_filters(queryset, cleaned_data)
        
        # Apply text search filters
        queryset = self._apply_text_filters(queryset, cleaned_data)
        
        # Apply character filters
        queryset = self._apply_character_filters(queryset, cleaned_data)
        
        # Apply edition filter
        queryset = queryset.filter(edition__lte=cleaned_data.get("edition"))
        
        # Apply tag filters
        queryset = self._apply_tag_filters(queryset, cleaned_data)
        
        # Apply character count filters
        queryset = self._apply_count_filters(queryset, cleaned_data)
        
        # Apply popularity filters
        queryset = self._apply_popularity_filters(queryset, cleaned_data)
        
        # Store results in session
        result_ids = list(queryset.values_list("pk", flat=True))
        self.request.session["queryset"] = result_ids
        
        if len(result_ids) == 0:
            self.request.session["num_results"] = 0
            
        return redirect("/script/search/results")

    def _apply_homebrewiness_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply homebrew filtering."""
        if not cleaned_data.get("include_hybrid"):
            queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HYBRID)
        if not cleaned_data.get("include_homebrew"):
            queryset = queryset.exclude(homebrewiness=models.Homebrewiness.HOMEBREW)
        return queryset

    def _apply_text_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply text-based filters using trigram similarity."""
        if cleaned_data.get("name"):
            queryset = queryset.annotate(
                name_similarity=TrigramSimilarity("script__name", cleaned_data["name"])
            ).filter(name_similarity__gt=0).order_by("-name_similarity")
            
        if cleaned_data.get("author"):
            queryset = queryset.annotate(
                author_similarity=TrigramSimilarity("author", cleaned_data["author"])
            ).filter(author_similarity__gt=0).order_by("-author_similarity")
            
        return queryset

    def _apply_character_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply character inclusion/exclusion filters."""
        if cleaned_data.get("includes_characters"):
            queryset = filters.include_characters(
                queryset,
                cleaned_data["includes_characters"]
            )
        if cleaned_data.get("excludes_characters"):
            queryset = filters.exclude_characters(
                queryset,
                cleaned_data["excludes_characters"]
            )
        return queryset

    def _apply_tag_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply tag filters with AND/OR logic."""
        tags = cleaned_data.get("tags")
        if not tags:
            return queryset
            
        if cleaned_data.get("tag_combinations") == "AND":
            for tag in tags:
                queryset = queryset.filter(tags=tag)
        else:
            queryset = queryset.filter(tags__in=tags)
            
        return queryset

    def _apply_count_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply character count filters."""
        count_fields = [
            ("number_of_townsfolk", "num_townsfolk"),
            ("number_of_outsiders", "num_outsiders"),
            ("number_of_minions", "num_minions"),
            ("number_of_demons", "num_demons"),
            ("number_of_fabled", "num_fabled"),
            ("number_of_travellers", "num_travellers"),
        ]
        
        for form_field, model_field in count_fields:
            values = cleaned_data.get(form_field)
            if values:
                queryset = queryset.filter(**{f"{model_field}__in": values})
                
        return queryset

    def _apply_popularity_filters(
        self,
        queryset: QuerySet,
        cleaned_data: Dict
    ) -> QuerySet:
        """Apply popularity-based filters."""
        min_likes = cleaned_data.get("minimum_number_of_likes")
        if min_likes:
            queryset = queryset.annotate(
                score=Count("script__votes")
            ).filter(score__gte=min_likes)
            
        min_favs = cleaned_data.get("minimum_number_of_favourites")
        if min_favs:
            queryset = queryset.annotate(
                num_favs=Count("script__favourites")
            ).filter(num_favs__gte=min_favs)
            
        min_comments = cleaned_data.get("minimum_number_of_comments")
        if min_comments:
            queryset = queryset.annotate(
                num_comments=Count("script__comments")
            ).filter(num_comments__gte=min_comments)
            
        return queryset


class AdvancedSearchResultsView(SingleTableView):
    """Display advanced search results."""
    
    model = models.ScriptVersion
    template_name = "scriptlist.html"
    table_pagination = {"per_page": 20}
    ordering = ["-pk"]
    script_view = None

    def get_queryset(self) -> QuerySet:
        """Get search results from session."""
        if self.request.session.get("queryset"):
            # Validate session IDs to prevent injection
            try:
                ids = validate_session_ids(self.request.session.get("queryset"))
            except ValidationError as e:
                logger.warning(f"Invalid session data in search results: {e}")
                return models.ScriptVersion.objects.none()
                
            # Preserve order from search
            preserved = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(ids)]
            )
            return models.ScriptVersion.objects.filter(pk__in=ids).order_by(preserved)
            
        elif self.request.session.get("num_results") == 0:
            return models.ScriptVersion.objects.none()
        else:
            # No search performed, show all
            return models.ScriptVersion.objects.all()

    def get_table_class(self):
        """Get appropriate table class based on authentication."""
        if self.request.user.is_authenticated:
            return tables.UserClocktowerTable
        return tables.ClocktowerTable


# Import needed classes for backwards compatibility
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.core.exceptions import ValidationError
