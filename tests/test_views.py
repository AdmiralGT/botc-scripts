"""
Tests for script views.
"""
import json
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from scripts import models


class ScriptUploadViewTest(TestCase):
    """Tests for script upload functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create test JSON content
        self.valid_json = [
            {"id": "washerwoman"},
            {"id": "librarian"},
            {"id": "investigator"},
            {"id": "chef"},
            {"id": "empath"},
            {"id": "fortuneteller"},
            {"id": "undertaker"},
            {"id": "monk"},
            {"id": "butler"},
            {"id": "drunk"},
            {"id": "recluse"},
            {"id": "poisoner"},
            {"id": "spy"},
            {"id": "imp"},
        ]
        
    def test_upload_valid_script_anonymous(self):
        """Test uploading a valid script as anonymous user."""
        json_file = SimpleUploadedFile(
            "test.json",
            json.dumps(self.valid_json).encode('utf-8'),
            content_type="application/json"
        )
        
        response = self.client.post(reverse('script_upload'), {
            'name': 'Test Script',
            'author': 'Test Author',
            'script_type': models.ScriptTypes.FULL,
            'version': '1.0',
            'content': json_file,
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Check script was created
        script = models.Script.objects.get(name='Test Script')
        self.assertIsNone(script.owner)
        
        # Check version was created
        version = script.versions.first()
        self.assertEqual(version.author, 'Test Author')
        self.assertEqual(version.version, '1.0')
        
    def test_upload_valid_script_authenticated(self):
        """Test uploading a valid script as authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        
        json_file = SimpleUploadedFile(
            "test.json",
            json.dumps(self.valid_json).encode('utf-8'),
            content_type="application/json"
        )
        
        response = self.client.post(reverse('script_upload'), {
            'name': 'My Script',
            'author': 'Test User',
            'script_type': models.ScriptTypes.FULL,
            'version': '1.0',
            'content': json_file,
            'anonymous': False,
        })
        
        self.assertEqual(response.status_code, 302)
        
        script = models.Script.objects.get(name='My Script')
        self.assertEqual(script.owner, self.user)
        
    def test_upload_invalid_json(self):
        """Test uploading invalid JSON is rejected."""
        json_file = SimpleUploadedFile(
            "test.json",
            b"not valid json",
            content_type="application/json"
        )
        
        response = self.client.post(reverse('script_upload'), {
            'name': 'Bad Script',
            'author': 'Test',
            'script_type': models.ScriptTypes.FULL,
            'version': '1.0',
            'content': json_file,
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'content', 
                           'Invalid JSON content: Expecting value: line 1 column 1 (char 0)')
        
    def test_upload_script_without_demon(self):
        """Test that scripts without demons are rejected."""
        json_without_demon = [
            {"id": "washerwoman"},
            {"id": "librarian"},
        ]
        
        json_file = SimpleUploadedFile(
            "test.json",
            json.dumps(json_without_demon).encode('utf-8'),
            content_type="application/json"
        )
        
        response = self.client.post(reverse('script_upload'), {
            'name': 'No Demon Script',
            'author': 'Test',
            'script_type': models.ScriptTypes.TEENSYVILLE,
            'version': '1.0',
            'content': json_file,
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Script must contain at least one Demon")
        
    def test_upload_duplicate_version(self):
        """Test that duplicate versions with different content are rejected."""
        # Create initial script
        script = models.Script.objects.create(name='Existing Script')
        models.ScriptVersion.objects.create(
            script=script,
            version='1.0',
            content=self.valid_json,
            script_type=models.ScriptTypes.FULL,
            num_townsfolk=8,
            num_outsiders=2,
            num_minions=2,
            num_demons=1,
            num_travellers=0,
            num_fabled=0,
        )
        
        # Try to upload different content with same version
        different_json = self.valid_json[:-1]  # Remove last character
        json_file = SimpleUploadedFile(
            "test.json",
            json.dumps(different_json).encode('utf-8'),
            content_type="application/json"
        )
        
        response = self.client.post(reverse('script_upload'), {
            'name': 'Existing Script',
            'author': 'Test',
            'script_type': models.ScriptTypes.FULL,
            'version': '1.0',
            'content': json_file,
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 
                          "Version 1.0 already exists. You cannot upload a different script with the same version number.")
        
    def test_file_size_limit(self):
        """Test that oversized files are rejected."""
        # Create a file larger than 5MB limit
        large_content = json.dumps([{"id": f"char{i}"} for i in range(100000)])
        large_file = SimpleUploadedFile(
            "large.json",
            large_content.encode('utf-8'),
            content_type="application/json"
        )
        
        with patch('scripts.validators_enhanced.MAX_JSON_SIZE', 100):  # Set tiny limit for testing
            response = self.client.post(reverse('script_upload'), {
                'name': 'Large Script',
                'author': 'Test',
                'script_type': models.ScriptTypes.FULL,
                'version': '1.0',
                'content': large_file,
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "exceeds maximum allowed size")


class ScriptViewTest(TestCase):
    """Tests for script display view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        self.script = models.Script.objects.create(
            name="Test Script",
            owner=self.user
        )
        
        self.version = models.ScriptVersion.objects.create(
            script=self.script,
            version="1.0",
            content=[{"id": "imp"}],
            script_type=models.ScriptTypes.TEENSYVILLE,
            num_townsfolk=0,
            num_outsiders=0,
            num_minions=0,
            num_demons=1,
            num_travellers=0,
            num_fabled=0,
        )
        
    def test_view_script(self):
        """Test viewing a script."""
        response = self.client.get(f'/script/{self.script.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Script")
        
    def test_view_specific_version(self):
        """Test viewing a specific version."""
        # Create another version
        version2 = models.ScriptVersion.objects.create(
            script=self.script,
            version="2.0",
            content=[{"id": "imp"}, {"id": "baron"}],
            script_type=models.ScriptTypes.TEENSYVILLE,
            num_townsfolk=0,
            num_outsiders=0,
            num_minions=1,
            num_demons=1,
            num_travellers=0,
            num_fabled=0,
        )
        
        response = self.client.get(f'/script/{self.script.pk}/1.0/')
        self.assertEqual(response.status_code, 200)
        # Should show version 1.0
        self.assertContains(response, "1.0")
        
    def test_delete_script_unauthorized(self):
        """Test that non-owners cannot delete scripts."""
        other_user = User.objects.create_user(
            username="otheruser",
            password="pass123"
        )
        self.client.login(username='otheruser', password='pass123')
        
        response = self.client.post(f'/script/{self.script.pk}/1.0/delete/')
        self.assertEqual(response.status_code, 403)
        
        # Script should still exist
        self.assertTrue(models.Script.objects.filter(pk=self.script.pk).exists())
        
    def test_delete_script_authorized(self):
        """Test that owners can delete their scripts."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(f'/script/{self.script.pk}/1.0/delete/')
        self.assertEqual(response.status_code, 302)
        
        # Version should be deleted, script should still exist (if other versions)
        self.assertFalse(
            models.ScriptVersion.objects.filter(
                script=self.script,
                version="1.0"
            ).exists()
        )


class VotingTest(TestCase):
    """Tests for voting functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        self.script = models.Script.objects.create(name="Test Script")
        
    def test_vote_requires_login(self):
        """Test that voting requires authentication."""
        response = self.client.post(f'/script/{self.script.pk}/vote/', {
            'next': f'/script/{self.script.pk}/'
        })
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        
    def test_vote_toggle(self):
        """Test that voting toggles on and off."""
        self.client.login(username='testuser', password='testpass123')
        
        # First vote should create
        response = self.client.post(f'/script/{self.script.pk}/vote/', {
            'next': f'/script/{self.script.pk}/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.votes.count(), 1)
        
        # Second vote should remove
        response = self.client.post(f'/script/{self.script.pk}/vote/', {
            'next': f'/script/{self.script.pk}/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.votes.count(), 0)
        
    def test_favourite_toggle(self):
        """Test that favouriting toggles on and off."""
        self.client.login(username='testuser', password='testpass123')
        
        # First favourite should create
        response = self.client.post(f'/script/{self.script.pk}/favourite/', {
            'next': f'/script/{self.script.pk}/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.favourites.count(), 1)
        
        # Second favourite should remove
        response = self.client.post(f'/script/{self.script.pk}/favourite/', {
            'next': f'/script/{self.script.pk}/'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.favourites.count(), 0)


class CommentTest(TestCase):
    """Tests for comment functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        self.script = models.Script.objects.create(name="Test Script")
        
    def test_create_comment_requires_login(self):
        """Test that creating comments requires authentication."""
        response = self.client.post('/comment/create/', {
            'script': self.script.pk,
            'comment': 'Test comment'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        
    def test_create_comment(self):
        """Test creating a comment."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/comment/create/', {
            'script': self.script.pk,
            'comment': 'This is a test comment'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.comments.count(), 1)
        
        comment = self.script.comments.first()
        self.assertEqual(comment.comment, 'This is a test comment')
        self.assertEqual(comment.user, self.user)
        
    def test_create_reply(self):
        """Test creating a reply to a comment."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create parent comment
        parent = models.Comment.objects.create(
            script=self.script,
            user=self.user,
            comment="Parent comment"
        )
        
        response = self.client.post('/comment/create/', {
            'script': self.script.pk,
            'parent': parent.pk,
            'comment': 'Reply comment'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.script.comments.count(), 2)
        
        reply = models.Comment.objects.get(comment='Reply comment')
        self.assertEqual(reply.parent, parent)
        
    def test_edit_comment(self):
        """Test editing a comment."""
        self.client.login(username='testuser', password='testpass123')
        
        comment = models.Comment.objects.create(
            script=self.script,
            user=self.user,
            comment="Original comment"
        )
        
        response = self.client.post(f'/comment/{comment.pk}/edit/', {
            'comment': 'Edited comment'
        })
        
        self.assertEqual(response.status_code, 302)
        
        comment.refresh_from_db()
        self.assertEqual(comment.comment, 'Edited comment')
        
    def test_cannot_edit_others_comment(self):
        """Test that users cannot edit other users' comments."""
        other_user = User.objects.create_user(
            username="other",
            password="pass123"
        )
        
        comment = models.Comment.objects.create(
            script=self.script,
            user=other_user,
            comment="Other's comment"
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(f'/comment/{comment.pk}/edit/', {
            'comment': 'Hacked comment'
        })
        
        self.assertEqual(response.status_code, 404)
        
        comment.refresh_from_db()
        self.assertEqual(comment.comment, "Other's comment")
        
    def test_delete_comment(self):
        """Test deleting a comment."""
        self.client.login(username='testuser', password='testpass123')
        
        comment = models.Comment.objects.create(
            script=self.script,
            user=self.user,
            comment="To be deleted"
        )
        
        response = self.client.post(f'/comment/{comment.pk}/delete/')
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            models.Comment.objects.filter(pk=comment.pk).exists()
        )
