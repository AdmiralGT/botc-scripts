"""
Enhanced API views with improved error handling and performance.
"""
import logging
from typing import List, Optional

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count, Q
from django.core.cache import cache

from scripts import models, serializers
from scripts.services import StatisticsService

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Script API endpoints.
    
    Provides list and detail views for scripts with filtering support.
    """
    queryset = models.ScriptVersion.objects.filter(latest=True)
    serializer_class = serializers.ScriptVersionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Apply filters from query parameters."""
        queryset = super().get_queryset()
        
        # Filter by homebrewiness
        homebrewiness = self.request.query_params.get('homebrewiness')
        if homebrewiness:
            try:
                queryset = queryset.filter(
                    homebrewiness=models.Homebrewiness[homebrewiness.upper()]
                )
            except KeyError:
                logger.warning(f"Invalid homebrewiness filter: {homebrewiness}")
        
        # Filter by script type
        script_type = self.request.query_params.get('script_type')
        if script_type:
            queryset = queryset.filter(script_type=script_type)
            
        # Filter by edition
        edition = self.request.query_params.get('edition')
        if edition:
            try:
                queryset = queryset.filter(edition__lte=int(edition))
            except ValueError:
                logger.warning(f"Invalid edition filter: {edition}")
                
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(script__name__icontains=search) |
                Q(author__icontains=search)
            )
            
        # Order by popularity if requested
        order = self.request.query_params.get('order_by')
        if order == 'popular':
            queryset = queryset.annotate(
                vote_count=Count('script__votes')
            ).order_by('-vote_count')
        elif order == 'recent':
            queryset = queryset.order_by('-created')
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar scripts to the given script."""
        script_version = self.get_object()
        
        # Check cache first
        cache_key = f"similar_scripts_{pk}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
            
        from scripts.services import ScriptService
        
        similar_scripts = []
        candidates = models.ScriptVersion.objects.filter(
            latest=True,
            homebrewiness=models.Homebrewiness.CLOCKTOWER
        ).exclude(pk=script_version.pk)[:100]  # Limit to 100 for performance
        
        for candidate in candidates:
            score = ScriptService.calculate_similarity(
                script_version.content,
                candidate.content,
                script_version.script_type == candidate.script_type
            )
            if score > 50:  # Only include if >50% similar
                similar_scripts.append({
                    'id': candidate.pk,
                    'name': candidate.script.name,
                    'similarity': score
                })
                
        # Sort by similarity and take top 10
        similar_scripts.sort(key=lambda x: x['similarity'], reverse=True)
        result = similar_scripts[:10]
        
        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending scripts based on recent activity."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get scripts with recent activity
        cutoff_date = timezone.now() - timedelta(days=7)
        
        trending = models.ScriptVersion.objects.filter(
            latest=True,
            script__votes__created__gte=cutoff_date
        ).annotate(
            recent_votes=Count('script__votes', filter=Q(
                script__votes__created__gte=cutoff_date
            ))
        ).order_by('-recent_votes')[:20]
        
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Character API endpoints."""
    queryset = models.ClocktowerCharacter.objects.all()
    serializer_class = serializers.CharacterSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Apply filters from query parameters."""
        queryset = super().get_queryset()
        
        # Filter by character type
        char_type = self.request.query_params.get('type')
        if char_type:
            queryset = queryset.filter(character_type=char_type)
            
        # Filter by edition
        edition = self.request.query_params.get('edition')
        if edition:
            try:
                queryset = queryset.filter(edition__lte=int(edition))
            except ValueError:
                logger.warning(f"Invalid edition filter: {edition}")
                
        return queryset
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for a character."""
        character = self.get_object()
        
        # Cache key for this character's stats
        cache_key = f"character_stats_{pk}"
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)
            
        # Calculate stats
        total_scripts = models.ScriptVersion.objects.filter(latest=True).count()
        usage_count = models.ScriptVersion.objects.filter(
            latest=True,
            content__contains=[{"id": character.character_id}]
        ).count()
        
        stats = {
            'character_id': character.character_id,
            'character_name': character.character_name,
            'usage_count': usage_count,
            'total_scripts': total_scripts,
            'usage_percentage': round((usage_count / total_scripts * 100), 2) if total_scripts > 0 else 0
        }
        
        # Cache for 1 hour
        cache.set(cache_key, stats, 3600)
        
        return Response(stats)


class EnhancedStatisticsAPI(APIView):
    """Enhanced statistics API with caching and better error handling."""
    
    permission_classes = []
    
    def get(self, request, format=None):
        """Get script statistics with various filters."""
        try:
            # Build queryset based on parameters
            if "all" in request.query_params:
                queryset = models.ScriptVersion.objects.all()
            else:
                queryset = models.ScriptVersion.objects.filter(latest=True)
                
            # Apply character filters
            queryset = self._apply_character_filters(queryset, request.query_params)
            
            # Get statistics
            stats = StatisticsService.get_character_statistics(
                queryset=queryset,
                use_cache=True
            )
            
            # Add total if requested
            if "total" in request.query_params:
                stats["total"] = queryset.count()
                
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error in statistics API: {e}")
            return Response(
                {"error": "An error occurred while generating statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _apply_character_filters(self, queryset, params):
        """Apply character-based filters to queryset."""
        # AND filters
        for character_id in params.getlist("character"):
            try:
                character = models.ClocktowerCharacter.objects.get(character_id=character_id)
                queryset = queryset.filter(
                    content__contains=[{"id": character.character_id}]
                )
            except models.ClocktowerCharacter.DoesNotExist:
                logger.warning(f"Character not found: {character_id}")
                
        # OR filters
        character_or_list = params.getlist("character_or")
        if character_or_list:
            or_query = Q()
            for character_id in character_or_list:
                try:
                    character = models.ClocktowerCharacter.objects.get(character_id=character_id)
                    or_query |= Q(content__contains=[{"id": character.character_id}])
                except models.ClocktowerCharacter.DoesNotExist:
                    logger.warning(f"Character not found: {character_id}")
                    
            if or_query:
                queryset = queryset.filter(or_query)
                
        # Exclude filters
        for character_id in params.getlist("exclude"):
            try:
                character = models.ClocktowerCharacter.objects.get(character_id=character_id)
                queryset = queryset.exclude(
                    content__contains=[{"id": character.character_id}]
                )
            except models.ClocktowerCharacter.DoesNotExist:
                logger.warning(f"Character not found: {character_id}")
                
        return queryset


class CollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Collection API endpoints."""
    
    serializer_class = serializers.CollectionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get collections based on user permissions."""
        if self.request.user.is_authenticated:
            # Show user's collections and public collections
            return models.Collection.objects.filter(
                Q(owner=self.request.user) | Q(public=True)
            ).distinct()
        else:
            # Only show public collections
            return models.Collection.objects.filter(public=True)
    
    def perform_create(self, serializer):
        """Set owner when creating collection."""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_script(self, request, pk=None):
        """Add a script to a collection."""
        collection = self.get_object()
        
        # Check ownership
        if collection.owner != request.user:
            return Response(
                {"error": "You don't have permission to modify this collection"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        script_id = request.data.get('script_id')
        if not script_id:
            return Response(
                {"error": "script_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            script_version = models.ScriptVersion.objects.get(pk=script_id)
            collection.scripts.add(script_version)
            return Response({"success": True})
        except models.ScriptVersion.DoesNotExist:
            return Response(
                {"error": "Script not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_script(self, request, pk=None):
        """Remove a script from a collection."""
        collection = self.get_object()
        
        # Check ownership
        if collection.owner != request.user:
            return Response(
                {"error": "You don't have permission to modify this collection"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        script_id = request.data.get('script_id')
        if not script_id:
            return Response(
                {"error": "script_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            script_version = models.ScriptVersion.objects.get(pk=script_id)
            collection.scripts.remove(script_version)
            return Response({"success": True})
        except models.ScriptVersion.DoesNotExist:
            return Response(
                {"error": "Script not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# Keep the old StatisticsAPI for backward compatibility but mark as deprecated
class StatisticsAPI(EnhancedStatisticsAPI):
    """
    DEPRECATED: Use EnhancedStatisticsAPI instead.
    Kept for backward compatibility.
    """
    
    def get(self, request, format=None):
        """Get statistics (deprecated)."""
        import warnings
        warnings.warn(
            "StatisticsAPI is deprecated. Use EnhancedStatisticsAPI instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return super().get(request, format)
