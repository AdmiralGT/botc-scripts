from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import override_settings
from django.db import models
from scripts.models import ScriptVersion
import time


class Command(BaseCommand):
    help = 'Test query performance before and after optimizations'
    
    def handle(self, *args, **options):
        self.stdout.write("Testing query performance...")
        
        # Test 1: List view performance
        self.test_list_view_performance()
        
        # Test 2: Individual script performance
        self.test_script_detail_performance()
        
        # Test 3: Query count analysis
        self.test_query_counts()
        
        self.stdout.write(
            self.style.SUCCESS('Performance testing completed!')
        )
    
    def test_list_view_performance(self):
        """Test the performance of list views"""
        self.stdout.write("Testing list view performance...")
        
        # Test old approach (for comparison)
        start_time = time.time()
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Simulate old approach with annotations
            old_scripts = list(
                ScriptVersion.objects
                .annotate(
                    num_tags=models.Count("tags", distinct=True),
                    score=models.Count("script__votes", distinct=True),
                    num_favs=models.Count("script__favourites", distinct=True),
                    num_comments=models.Count("script__comments", distinct=True)
                )
                .filter(latest=True)[:20]
            )
            
            # Access related data to trigger N+1 queries
            for script in old_scripts:
                script.script.name  # N+1 query
                list(script.tags.all())  # N+1 query
            
            old_query_count = len(connection.queries)
        
        old_time = time.time() - start_time
        
        # Test new approach
        start_time = time.time()
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Use optimized approach
            new_scripts = list(
                ScriptVersion.objects.for_list_view()
                .filter(latest=True)[:20]
            )
            
            # Access related data (should not trigger additional queries)
            for script in new_scripts:
                script.script.name  # No additional query
                list(script.tags.all())  # No additional query
            
            new_query_count = len(connection.queries)
        
        new_time = time.time() - start_time
        
        self.stdout.write(f"Old approach: {old_query_count} queries, {old_time:.2f}s")
        self.stdout.write(f"New approach: {new_query_count} queries, {new_time:.2f}s")
        
        if old_query_count > 0:
            improvement = (old_query_count - new_query_count) / old_query_count * 100
            self.stdout.write(f"Query reduction: {improvement:.1f}%")
        
        if old_time > 0:
            time_improvement = (old_time - new_time) / old_time * 100
            self.stdout.write(f"Time improvement: {time_improvement:.1f}%")
    
    def test_script_detail_performance(self):
        """Test individual script page performance"""
        self.stdout.write("Testing script detail performance...")
        
        # Get a script to test with
        script = ScriptVersion.objects.filter(latest=True).first()
        if not script:
            self.stdout.write("No scripts found for testing")
            return
        
        # Test old approach
        start_time = time.time()
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Simulate old approach without prefetching
            from scripts.models import Script
            test_script = Script.objects.get(pk=script.script.pk)
            
            # Access related data (triggers N+1 queries)
            versions = list(test_script.versions.all())
            for version in versions:
                list(version.tags.all())  # N+1 query
            
            comments = list(test_script.comments.all())
            for comment in comments:
                comment.user.username  # N+1 query
            
            old_query_count = len(connection.queries)
        
        old_time = time.time() - start_time
        
        # Test new approach with prefetching
        start_time = time.time()
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Use optimized approach from ScriptView
            from scripts.views import ScriptView
            view = ScriptView()
            test_script = view.get_queryset().get(pk=script.script.pk)
            
            # Access related data (should not trigger additional queries)
            versions = list(test_script.versions.all())
            for version in versions:
                list(version.tags.all())  # No additional query
            
            comments = list(test_script.comments.all())
            for comment in comments:
                comment.user.username  # No additional query
            
            new_query_count = len(connection.queries)
        
        new_time = time.time() - start_time
        
        self.stdout.write(f"Script detail old: {old_query_count} queries, {old_time:.2f}s")
        self.stdout.write(f"Script detail new: {new_query_count} queries, {new_time:.2f}s")
        
        if old_query_count > 0:
            improvement = (old_query_count - new_query_count) / old_query_count * 100
            self.stdout.write(f"Query reduction: {improvement:.1f}%")
    
    def test_query_counts(self):
        """Analyze query patterns"""
        self.stdout.write("Analyzing query patterns...")
        
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Test the most common page load
            scripts = list(
                ScriptVersion.objects.for_list_view()
                .filter(latest=True)[:20]
            )
            
            # Force evaluation of relationships
            for script in scripts:
                script.script.name
                script.script.owner
                list(script.tags.all())
            
            total_queries = len(connection.queries)
            
            self.stdout.write(f"Total queries for 20 scripts: {total_queries}")
            
            if total_queries <= 5:
                self.stdout.write(self.style.SUCCESS("Excellent! Very few queries."))
            elif total_queries <= 10:
                self.stdout.write(self.style.SUCCESS("Good! Reasonable query count."))
            elif total_queries <= 20:
                self.stdout.write(self.style.WARNING("Moderate query count. Could be better."))
            else:
                self.stdout.write(self.style.ERROR("High query count. N+1 issues likely remain."))
