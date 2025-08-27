"""
Statistics views.
"""
import logging
from typing import Dict, Any

from django.views import generic
from django_filters.views import FilterView

from scripts import models, filters
from scripts.services import StatisticsService

logger = logging.getLogger(__name__)


class StatisticsView(generic.ListView, FilterView):
    """View for displaying script statistics."""
    
    model = models.ScriptVersion
    template_name = "statistics.html"
    filterset_class = filters.StatisticsFilter
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Get statistics context data."""
        self.object_list = super().get_queryset()
        context = super().get_context_data(**kwargs)
        
        # Determine queryset based on filters
        queryset = self._get_filtered_queryset()
        
        # Handle character-specific statistics
        stats_character = self._get_stats_character()
        if stats_character:
            context["character"] = stats_character
            queryset = queryset.filter(
                content__contains=[{"id": stats_character.character_id}]
            )
            
        # Handle tag-specific statistics
        tag = self._get_stats_tag()
        if tag:
            context["tag"] = tag
            queryset = queryset.filter(tags__in=[tag])
            
        # Get statistics from service
        context["total"] = queryset.count()
        
        if context["total"] > 0:
            # Character statistics
            character_stats = StatisticsService.get_character_statistics(
                queryset=queryset,
                limit=self._get_display_limit()
            )
            
            # Add character statistics to context
            for char_type in models.CharacterType:
                type_value = char_type.value
                context[type_value] = character_stats["most_common"].get(type_value, [])
                context[f"{type_value}least"] = character_stats["least_common"].get(type_value, [])
                
            # Add distribution statistics
            context["num_count"] = character_stats["distribution"]
            
            # Add popularity statistics if requested
            if self.request.GET.get("show_popularity"):
                popularity_stats = StatisticsService.get_script_popularity_stats(queryset)
                context["popularity"] = popularity_stats
                
        return context
    
    def _get_filtered_queryset(self):
        """Build filtered queryset based on request parameters."""
        # Base queryset
        if "all" in self.request.GET:
            queryset = models.ScriptVersion.objects.all()
        else:
            queryset = models.ScriptVersion.objects.filter(latest=True)
            
        # Filter to clocktower scripts only
        queryset = queryset.filter(homebrewiness=models.Homebrewiness.CLOCKTOWER)
        
        # Apply user filters if authenticated
        if self.request.user.is_authenticated:
            context = {"filter": self.get_filterset(self.get_filterset_class())}
            if "is_owner" in self.request.GET:
                queryset = queryset.filter(script__owner=self.request.user)
                
        # Apply edition filter
        if "edition" in self.request.GET:
            try:
                edition = models.Edition(int(self.request.GET.get("edition")))
                queryset = queryset.filter(edition__lte=edition)
            except (ValueError, TypeError):
                logger.warning(f"Invalid edition value: {self.request.GET.get('edition')}")
                
        return queryset
    
    def _get_stats_character(self):
        """Get character for character-specific statistics."""
        if "character" in self.kwargs:
            try:
                return models.ClocktowerCharacter.objects.get(
                    character_id=self.kwargs.get("character")
                )
            except models.ClocktowerCharacter.DoesNotExist:
                raise Http404("Character not found")
        return None
    
    def _get_stats_tag(self):
        """Get tag for tag-specific statistics."""
        if "tags" in self.kwargs:
            try:
                return models.ScriptTag.objects.get(pk=self.kwargs.get("tags"))
            except (models.ScriptTag.DoesNotExist, ValueError):
                return None
                
        if "tags" in self.request.GET:
            try:
                return models.ScriptTag.objects.get(pk=self.request.GET.get("tags"))
            except (models.ScriptTag.DoesNotExist, ValueError):
                return None
                
        return None
    
    def _get_display_limit(self) -> int:
        """Get number of characters to display."""
        try:
            limit = int(self.request.GET.get("num", 25))
            return max(1, min(limit, 100))  # Between 1 and 100
        except (ValueError, TypeError):
            return 25


# Import Http404 for error handling
from django.http import Http404
