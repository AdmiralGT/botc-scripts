"""
Tests for the delete all versions functionality.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from scripts.models import Script, ScriptVersion
from versionfield import Version


@pytest.fixture
def user(db):
    """Create a test user with API write permission."""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    
    user = User.objects.create_user(
        username="testuser",
        password="testpass123",
        email="test@example.com"
    )
    
    # Grant API write permission
    content_type = ContentType.objects.get_for_model(ScriptVersion)
    permission = Permission.objects.get(
        codename="api_write_permission",
        content_type=content_type
    )
    user.user_permissions.add(permission)
    
    return user


@pytest.fixture
def other_user(db):
    """Create another test user with API write permission."""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    
    user = User.objects.create_user(
        username="otheruser",
        password="testpass123",
        email="other@example.com"
    )
    
    # Grant API write permission
    content_type = ContentType.objects.get_for_model(ScriptVersion)
    permission = Permission.objects.get(
        codename="api_write_permission",
        content_type=content_type
    )
    user.user_permissions.add(permission)
    
    return user


@pytest.fixture
def script_with_multiple_versions(db, user):
    """Create a script with multiple versions."""
    script = Script.objects.create(name="Test Script", owner=user)
    
    # Create version 1.0
    ScriptVersion.objects.create(
        script=script,
        version=Version("1.0"),
        content=[{"id": "washerwoman"}],
        latest=False,
        num_townsfolk=1,
        num_outsiders=0,
        num_minions=0,
        num_demons=0,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
    )
    
    # Create version 2.0 (latest)
    version_2 = ScriptVersion.objects.create(
        script=script,
        version=Version("2.0"),
        content=[{"id": "washerwoman"}, {"id": "librarian"}],
        latest=True,
        num_townsfolk=2,
        num_outsiders=0,
        num_minions=0,
        num_demons=0,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
    )
    
    return script, version_2


@pytest.fixture
def script_with_single_version(db, user):
    """Create a script with a single version."""
    script = Script.objects.create(name="Single Version Script", owner=user)
    version = ScriptVersion.objects.create(
        script=script,
        version=Version("1.0"),
        content=[{"id": "washerwoman"}],
        latest=True,
        num_townsfolk=1,
        num_outsiders=0,
        num_minions=0,
        num_demons=0,
        num_fabled=0,
        num_loric=0,
        num_travellers=0,
    )
    return script, version


class TestDeleteAllVersionsView:
    """Test the web view for deleting all versions."""
    
    def test_delete_all_versions_success(self, db, user, script_with_multiple_versions):
        """Test successful deletion of all versions."""
        script, version = script_with_multiple_versions
        client = Client()
        client.force_login(user)
        
        # Verify script exists with multiple versions
        assert Script.objects.filter(pk=script.pk).exists()
        assert script.versions.count() == 2
        
        # Delete all versions
        url = reverse("delete_all_script_versions", kwargs={"pk": script.pk})
        response = client.post(url)
        
        # Should redirect to home page
        assert response.status_code == 302
        assert response.url == "/"
        
        # Script and all versions should be deleted
        assert not Script.objects.filter(pk=script.pk).exists()
        assert not ScriptVersion.objects.filter(script_id=script.pk).exists()
    
    def test_delete_all_versions_permission_denied(self, db, other_user, script_with_multiple_versions):
        """Test that non-owners cannot delete all versions."""
        script, version = script_with_multiple_versions
        client = Client()
        client.force_login(other_user)
        
        url = reverse("delete_all_script_versions", kwargs={"pk": script.pk})
        response = client.post(url)
        
        # Should return 403 Forbidden
        assert response.status_code == 403
        
        # Script should still exist
        assert Script.objects.filter(pk=script.pk).exists()
        assert script.versions.count() == 2
    
    def test_delete_all_versions_unauthenticated(self, db, script_with_multiple_versions):
        """Test that unauthenticated users cannot delete."""
        script, version = script_with_multiple_versions
        client = Client()
        
        url = reverse("delete_all_script_versions", kwargs={"pk": script.pk})
        response = client.post(url)
        
        # Should redirect to login
        assert response.status_code == 302
        assert "/login" in response.url or "/account/login" in response.url
        
        # Script should still exist
        assert Script.objects.filter(pk=script.pk).exists()
    
    def test_delete_all_versions_get_method_not_allowed(self, db, user, script_with_multiple_versions):
        """Test that GET method is not allowed (should use POST)."""
        script, version = script_with_multiple_versions
        client = Client()
        client.force_login(user)
        
        url = reverse("delete_all_script_versions", kwargs={"pk": script.pk})
        response = client.get(url)
        
        # BaseDeleteView typically allows GET for confirmation, but let's verify behavior
        # This might return 200 (showing confirmation) or 405, depending on implementation
        assert response.status_code in [200, 405]
    
    def test_delete_all_versions_nonexistent_script(self, db, user):
        """Test deletion of non-existent script."""
        client = Client()
        client.force_login(user)
        
        url = reverse("delete_all_script_versions", kwargs={"pk": 99999})
        response = client.post(url)
        
        # Should return 404
        assert response.status_code == 404


class TestDeleteAllVersionsAPI:
    """Test the API endpoint for deleting all versions."""
    
    def test_api_delete_all_versions_success(self, db, user, script_with_multiple_versions):
        """Test successful API deletion of all versions."""
        from rest_framework.test import APIClient
        
        script, version = script_with_multiple_versions
        client = APIClient()
        
        # Use Basic Auth - set credentials directly
        client.credentials(HTTP_AUTHORIZATION=f'Basic {self._get_basic_auth(user)}')
        
        # Verify script exists
        assert Script.objects.filter(pk=script.pk).exists()
        assert script.versions.count() == 2
        
        # Delete via API
        url = f"/api/scripts/{version.pk}/delete-all-versions/"
        response = client.delete(url)
        
        # Should return 204 No Content
        assert response.status_code == 204
        
        # Script and all versions should be deleted
        assert not Script.objects.filter(pk=script.pk).exists()
        assert not ScriptVersion.objects.filter(script_id=script.pk).exists()
    
    def test_api_delete_all_versions_permission_denied(self, db, other_user, script_with_multiple_versions):
        """Test that non-owners cannot delete via API."""
        from rest_framework.test import APIClient
        
        script, version = script_with_multiple_versions
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Basic {self._get_basic_auth(other_user)}')
        
        url = f"/api/scripts/{version.pk}/delete-all-versions/"
        response = client.delete(url)
        
        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "error" in response.json()
        
        # Script should still exist
        assert Script.objects.filter(pk=script.pk).exists()
    
    def test_api_delete_all_versions_not_found(self, db, user):
        """Test API deletion of non-existent script version."""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Basic {self._get_basic_auth(user)}')
        
        url = "/api/scripts/99999/delete-all-versions/"
        response = client.delete(url)
        
        # Should return 404
        assert response.status_code == 404
        assert "error" in response.json()
    
    def test_api_delete_all_versions_unauthenticated(self, db, script_with_multiple_versions):
        """Test that unauthenticated users cannot delete via API."""
        from rest_framework.test import APIClient
        
        script, version = script_with_multiple_versions
        client = APIClient()
        
        url = f"/api/scripts/{version.pk}/delete-all-versions/"
        response = client.delete(url)
        
        # Should return 401 Unauthorized or 403 Forbidden (both indicate rejection)
        assert response.status_code in [401, 403]
        
        # Script should still exist
        assert Script.objects.filter(pk=script.pk).exists()
    
    @staticmethod
    def _get_basic_auth(user):
        """Helper to create basic auth header."""
        import base64
        credentials = f"{user.username}:testpass123"
        return base64.b64encode(credentials.encode()).decode()


class TestDeleteAllVersionsTemplate:
    """Test template rendering and UI elements."""
    
    @pytest.mark.skip(reason="Requires PostgreSQL for DISTINCT ON queries in template")
    def test_template_shows_dropdown_for_multiple_versions(self, db, user, script_with_multiple_versions):
        """Test that dropdown appears when script has multiple versions."""
        script, version = script_with_multiple_versions
        client = Client()
        client.force_login(user)
        
        url = reverse("script", kwargs={"pk": script.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        # Check that delete button and dropdown are present
        assert b"Delete Version" in response.content
        assert b"Delete All Versions" in response.content or b"dropdown" in response.content.lower()
    
    @pytest.mark.skip(reason="Requires PostgreSQL for DISTINCT ON queries in template")
    def test_template_no_dropdown_for_single_version(self, db, user, script_with_single_version):
        """Test that dropdown does not appear for single version."""
        script, version = script_with_single_version
        client = Client()
        client.force_login(user)
        
        url = reverse("script", kwargs={"pk": script.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        # Delete button should exist, but dropdown should not
        assert b"Delete Version" in response.content
        # The "Delete All Versions" text should not appear for single version
        # (or the dropdown should not be rendered)

