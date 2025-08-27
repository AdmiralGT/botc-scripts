Homebrewiness.CLOCKTOWER,
            latest=True,
        )
        
        # Create some characters
        self.imp = models.ClocktowerCharacter.objects.create(
            character_id="imp",
            character_name="Imp",
            character_type=models.CharacterType.DEMON,
            edition=models.Edition.BASE,
            ability="Test ability"
        )
        
    def test_get_character_statistics(self):
        """Test getting character statistics."""
        queryset = models.ScriptVersion.objects.filter(latest=True)
        
        stats = StatisticsService.get_character_statistics(
            queryset=queryset,
            limit=10,
            use_cache=False
        )
        
        self.assertEqual(stats['total_scripts'], 1)
        self.assertIn('by_type', stats)
        self.assertIn('most_common', stats)
        self.assertIn('distribution', stats)
        
    def test_get_script_popularity_stats(self):
        """Test getting popularity statistics."""
        # Add some votes and favorites
        user = User.objects.create_user(username="test", password="test")
        models.Vote.objects.create(parent=self.script, user=user)
        models.Favourite.objects.create(parent=self.script, user=user)
        
        stats = StatisticsService.get_script_popularity_stats(use_cache=False)
        
        self.assertEqual(stats['total_scripts'], 1)
        self.assertEqual(stats['total_votes'], 1)
        self.assertEqual(stats['total_favorites'], 1)
        
    def test_get_tag_statistics(self):
        """Test getting tag statistics."""
        tag = models.ScriptTag.objects.create(
            name="Test Tag",
            public=True,
            order=1
        )
        self.version.tags.add(tag)
        
        stats = StatisticsService.get_tag_statistics(use_cache=False)
        
        self.assertEqual(stats['total_tags'], 1)
        self.assertEqual(stats['public_tags'], 1)
        self.assertEqual(len(stats['tag_usage']), 1)
        
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # This should not raise an error
        StatisticsService.invalidate_statistics_cache()
        
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key = StatisticsService._generate_cache_key("test", "param1", "param2")
        self.assertIn("stats:", key)
        self.assertIn("test", key)
        
        # Test with long key
        long_param = "x" * 300
        key = StatisticsService._generate_cache_key("test", long_param)
        # Should be hashed
        self.assertTrue(len(key) < 250)


# Import User for tests
from django.contrib.auth.models import User
