from django.db import models


class ScriptViewManager(models.Manager):
    def get_queryset(self):
        # Remove expensive annotations from base queryset
        # These are only added when specifically needed
        return super().get_queryset()
    
    def for_list_view(self, include_stats=False, ordering=None):
        """
        Optimized queryset for list views with conditional stats.
        Only adds expensive stats when sorting requires them.
        """
        queryset = (
            self.get_queryset()
            .select_related('script', 'script__owner')  # Prevent N+1 for script access
            .prefetch_related('tags')                   # Prevent N+1 for tags
            .only(
                # Only load fields actually displayed in lists
                'id', 'version', 'script_type', 'author', 'created', 'latest',
                'homebrewiness', 'edition', 'num_demons', 'num_townsfolk',
                'num_outsiders', 'num_minions', 'num_fabled', 'num_travellers',
                'script__id', 'script__name', 'script__owner__username'
            )
        )
        
        # Only add expensive stats if sorting by them or explicitly requested
        if include_stats or self._needs_stats_for_sorting(ordering):
            queryset = queryset.annotate(
                num_tags=models.Count("tags", distinct=True),
                score=models.Count("script__votes", distinct=True),
                num_favs=models.Count("script__favourites", distinct=True),
                num_comments=models.Count("script__comments", distinct=True)
            )
        
        return queryset
    
    def _needs_stats_for_sorting(self, ordering):
        """Check if the ordering requires expensive stats"""
        if not ordering:
            return False
            
        # Convert ordering to list if it's a string
        if isinstance(ordering, str):
            ordering = [ordering]
        
        # Check if any ordering field requires stats
        stats_fields = {'score', '-score', 'num_favs', '-num_favs', 'num_comments', '-num_comments', 'num_tags', '-num_tags'}
        return any(field in stats_fields for field in ordering)
    
    def with_stats(self):
        """Add expensive stats annotations when explicitly needed"""
        return (
            self.get_queryset()
            .select_related('script', 'script__owner')
            .prefetch_related('tags')
            .annotate(
                num_tags=models.Count("tags", distinct=True),
                score=models.Count("script__votes", distinct=True),
                num_favs=models.Count("script__favourites", distinct=True),
                num_comments=models.Count("script__comments", distinct=True)
            )
        )


class CollectionManager(models.Manager):
    def get_queryset(self):
        qs = super(CollectionManager, self).get_queryset().annotate(scripts_in_collection=models.Count("scripts"))
        return qs
