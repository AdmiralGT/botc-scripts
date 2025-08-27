"""
Service for statistics-related business logic.
"""
import logging
from typing import Dict, List, Optional, Any
from collections import Counter
from django.db.models import QuerySet, Count, Q, Prefetch
from django.core.cache import cache as django_cache

from scripts import models

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service class for statistics operations."""
    
    STATS_CACHE_PREFIX = "stats"
    STATS_CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_character_statistics(
        cls,
        queryset: Optional[QuerySet] = None,
        character_type: Optional[models.CharacterType] = None,
        limit: int = 25,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive character usage statistics.
        
        Args:
            queryset: Optional QuerySet to analyze (defaults to latest scripts)
            character_type: Optional filter by character type
            limit: Maximum number of results per category
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing statistics data
        """
        if queryset is None:
            queryset = models.ScriptVersion.objects.filter(
                latest=True,
                homebrewiness=models.Homebrewiness.CLOCKTOWER
            )
            
        # Generate cache key
        cache_key = cls._generate_cache_key(
            "character_stats",
            queryset.query.__str__(),
            character_type,
            limit
        )
        
        if use_cache:
            cached_result = django_cache.get(cache_key)
            if cached_result:
                return cached_result
                
        # Calculate statistics
        result = cls._calculate_character_statistics(
            queryset,
            character_type,
            limit
        )
        
        # Cache the result
        django_cache.set(cache_key, result, cls.STATS_CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def _calculate_character_statistics(
        cls,
        queryset: QuerySet,
        character_type: Optional[models.CharacterType],
        limit: int
    ) -> Dict[str, Any]:
        """
        Internal method to calculate character statistics.
        """
        stats = {
            'total_scripts': queryset.count(),
            'by_type': {},
            'most_common': {},
            'least_common': {},
            'distribution': {}
        }
        
        if stats['total_scripts'] == 0:
            return stats
            
        # Get all characters, optionally filtered by type
        characters = models.ClocktowerCharacter.objects.all()
        if character_type:
            characters = characters.filter(character_type=character_type)
            
        # Use prefetch to optimize queries
        queryset = queryset.prefetch_related(
            Prefetch('script__versions', queryset=models.ScriptVersion.objects.all())
        )
        
        # Count character occurrences
        character_counts = Counter()
        
        for character in characters.iterator():
            count = queryset.filter(
                content__contains=[{"id": character.character_id}]
            ).count()
            if count > 0:
                character_counts[character] = count
                
        # Process results by character type
        for c_type in models.CharacterType:
            type_chars = [
                (char, count) for char, count in character_counts.items()
                if char.character_type == c_type.value
            ]
            
            if type_chars:
                sorted_chars = sorted(type_chars, key=lambda x: x[1], reverse=True)
                stats['most_common'][c_type.value] = sorted_chars[:limit]
                stats['least_common'][c_type.value] = sorted_chars[-limit:]
                
        # Calculate distribution statistics
        stats['distribution'] = cls._calculate_distribution_stats(queryset)
        
        return stats
    
    @classmethod
    def _calculate_distribution_stats(cls, queryset: QuerySet) -> Dict[str, Dict]:
        """
        Calculate distribution statistics for character counts.
        """
        distribution = {}
        
        for field, label in [
            ('num_townsfolk', 'Townsfolk'),
            ('num_outsiders', 'Outsiders'),
            ('num_minions', 'Minions'),
            ('num_demons', 'Demons'),
            ('num_travellers', 'Travellers'),
            ('num_fabled', 'Fabled')
        ]:
            # Get min and max values
            aggregated = queryset.aggregate(
                min_val=models.Min(field),
                max_val=models.Max(field),
                avg_val=models.Avg(field)
            )
            
            if aggregated['min_val'] is not None:
                dist = {}
                for i in range(aggregated['min_val'], aggregated['max_val'] + 1):
                    count = queryset.filter(**{field: i}).count()
                    if count > 0:
                        dist[str(i)] = count
                        
                distribution[label] = {
                    'counts': dist,
                    'min': aggregated['min_val'],
                    'max': aggregated['max_val'],
                    'average': round(aggregated['avg_val'], 2) if aggregated['avg_val'] else 0
                }
                
        return distribution
    
    @classmethod
    def get_script_popularity_stats(
        cls,
        queryset: Optional[QuerySet] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get popularity statistics for scripts.
        
        Args:
            queryset: Optional QuerySet to analyze
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing popularity statistics
        """
        if queryset is None:
            queryset = models.ScriptVersion.objects.filter(latest=True)
            
        cache_key = cls._generate_cache_key(
            "popularity_stats",
            queryset.query.__str__()
        )
        
        if use_cache:
            cached_result = django_cache.get(cache_key)
            if cached_result:
                return cached_result
                
        # Calculate popularity metrics
        stats = {
            'total_scripts': queryset.count(),
            'total_votes': 0,
            'total_favorites': 0,
            'total_comments': 0,
            'most_voted': [],
            'most_favorited': [],
            'most_discussed': []
        }
        
        # Annotate with counts
        annotated = queryset.annotate(
            vote_count=Count('script__votes', distinct=True),
            favorite_count=Count('script__favourites', distinct=True),
            comment_count=Count('script__comments', distinct=True)
        )
        
        # Get totals
        totals = annotated.aggregate(
            total_votes=models.Sum('vote_count'),
            total_favorites=models.Sum('favorite_count'),
            total_comments=models.Sum('comment_count')
        )
        
        stats.update({
            'total_votes': totals['total_votes'] or 0,
            'total_favorites': totals['total_favorites'] or 0,
            'total_comments': totals['total_comments'] or 0
        })
        
        # Get top scripts by each metric
        stats['most_voted'] = list(
            annotated.order_by('-vote_count')[:10]
            .values('script__name', 'script__pk', 'vote_count')
        )
        
        stats['most_favorited'] = list(
            annotated.order_by('-favorite_count')[:10]
            .values('script__name', 'script__pk', 'favorite_count')
        )
        
        stats['most_discussed'] = list(
            annotated.order_by('-comment_count')[:10]
            .values('script__name', 'script__pk', 'comment_count')
        )
        
        # Cache the result
        django_cache.set(cache_key, stats, cls.STATS_CACHE_TIMEOUT)
        
        return stats
    
    @classmethod
    def get_tag_statistics(
        cls,
        queryset: Optional[QuerySet] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get statistics about tag usage.
        
        Args:
            queryset: Optional QuerySet to analyze
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing tag statistics
        """
        if queryset is None:
            queryset = models.ScriptVersion.objects.filter(latest=True)
            
        cache_key = cls._generate_cache_key("tag_stats", queryset.query.__str__())
        
        if use_cache:
            cached_result = django_cache.get(cache_key)
            if cached_result:
                return cached_result
                
        # Get all tags with their usage counts
        tags = models.ScriptTag.objects.annotate(
            usage_count=Count('scriptversion', distinct=True)
        ).filter(usage_count__gt=0).order_by('-usage_count')
        
        stats = {
            'total_tags': tags.count(),
            'tag_usage': list(tags.values('name', 'usage_count', 'style')),
            'most_used': list(tags[:10].values('name', 'usage_count')),
            'public_tags': tags.filter(public=True).count(),
            'private_tags': tags.filter(public=False).count()
        }
        
        # Cache the result
        django_cache.set(cache_key, stats, cls.STATS_CACHE_TIMEOUT)
        
        return stats
    
    @staticmethod
    def _generate_cache_key(*args) -> str:
        """Generate a cache key from arguments."""
        import hashlib
        key_parts = [str(arg) for arg in args if arg is not None]
        key_str = ":".join(key_parts)
        # Use hash for long keys
        if len(key_str) > 200:
            key_str = hashlib.md5(key_str.encode()).hexdigest()
        return f"{StatisticsService.STATS_CACHE_PREFIX}:{key_str}"
    
    @classmethod
    def invalidate_statistics_cache(cls) -> None:
        """Invalidate all statistics caches."""
        # This is a simple implementation - in production you might want
        # to use cache tags or a more sophisticated invalidation strategy
        django_cache.delete_many(
            django_cache.keys(f"{cls.STATS_CACHE_PREFIX}:*")
        )
