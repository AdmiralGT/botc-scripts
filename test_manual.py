#!/usr/bin/env python
"""
Quick manual testing script for delete all versions functionality.
Run this with: python manage.py shell < test_manual.py
Or copy-paste into Django shell.
"""
from scripts.models import Script, ScriptVersion
from django.contrib.auth.models import User
from versionfield import Version

# Create or get a test user
user, created = User.objects.get_or_create(
    username="testuser",
    defaults={"email": "test@example.com"}
)
if created:
    user.set_password("testpass123")
    user.save()
    print(f"Created user: {user.username}")

# Create a test script with multiple versions
script, created = Script.objects.get_or_create(
    name="Test Script for Deletion",
    defaults={"owner": user}
)
if created:
    print(f"Created script: {script.name} (ID: {script.pk})")
else:
    print(f"Using existing script: {script.name} (ID: {script.pk})")

# Check current versions
current_versions = script.versions.count()
print(f"Current versions: {current_versions}")

# Create multiple versions if needed
if current_versions < 2:
    for i, version_str in enumerate(["1.0", "2.0", "3.0"], 1):
        ScriptVersion.objects.get_or_create(
            script=script,
            version=Version(version_str),
            defaults={
                "content": [{"id": "washerwoman"}] * i,
                "latest": (i == 3),  # Only last one is latest
                "num_townsfolk": i,
                "num_outsiders": 0,
                "num_minions": 0,
                "num_demons": 0,
                "num_fabled": 0,
                "num_loric": 0,
                "num_travellers": 0,
            }
        )
    print(f"Created test versions. Total versions: {script.versions.count()}")

# Display script info
print("\n" + "="*50)
print("SCRIPT INFORMATION")
print("="*50)
print(f"Script ID: {script.pk}")
print(f"Script Name: {script.name}")
print(f"Owner: {script.owner.username if script.owner else 'None'}")
print(f"Number of versions: {script.versions.count()}")
print("\nVersions:")
for v in script.versions.all().order_by("version"):
    print(f"  - Version {v.version} (PK: {v.pk}, Latest: {v.latest})")

print("\n" + "="*50)
print("TESTING INSTRUCTIONS")
print("="*50)
print("1. Web UI Test:")
print(f"   - Go to: http://localhost:8000/script/{script.pk}")
print("   - Look for 'Delete Version' button with dropdown")
print("   - Click dropdown and select 'Delete All Versions'")
print("   - Confirm deletion")
print("   - Should redirect to home page")
print("\n2. API Test:")
print(f"   curl -X DELETE -u {user.username}:testpass123 \\")
print(f"        http://localhost:8000/api/scripts/{script.versions.first().pk}/delete-all-versions/")
print("\n3. Verify deletion:")
print(f"   Script.objects.filter(pk={script.pk}).exists()  # Should be False")

