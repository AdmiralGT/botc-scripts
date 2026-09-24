# Testing Guide: Delete All Versions Feature

This guide covers both manual testing and automated testing for the new "Delete All Versions" functionality.

## Manual Testing

### Prerequisites
1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Ensure you have:
   - A user account with at least one script that has multiple versions
   - Access to the Django admin or ability to create test data

### Test Scenario 1: Web UI - Delete All Versions (Multiple Versions)

1. **Navigate to a script page** that has 2+ versions:
   - Go to: `http://localhost:8000/script/<script_id>`
   - Or find a script you own with multiple versions

2. **Verify the dropdown appears**:
   - Look for the "Delete Version" button
   - If the script has multiple versions, you should see a dropdown arrow next to it
   - Click the dropdown to see "Delete All Versions" option

3. **Test the deletion**:
   - Click "Delete All Versions" from the dropdown
   - A modal should appear asking for confirmation
   - The modal should show: "Are you sure you want to delete all X versions of 'Script Name'?"
   - Click "Delete All Versions" in the modal
   - You should be redirected to the home page (`/`)
   - Verify the script no longer exists in the database

### Test Scenario 2: Web UI - Single Version Script

1. **Navigate to a script page** that has only 1 version:
   - The "Delete Version" button should NOT have a dropdown
   - Only the single version deletion option should be available

### Test Scenario 3: Web UI - Permission Check

1. **Try to delete a script you don't own**:
   - Navigate to a script owned by another user
   - You should NOT see the delete button at all (if `can_delete` is False)
   - Or if you somehow access the URL directly, you should get a 403 Forbidden error

### Test Scenario 4: API Endpoint

1. **Get authentication credentials**:
   ```bash
   # You'll need Basic Auth credentials for a user who owns a script
   ```

2. **Test the API endpoint**:
   ```bash
   # Replace <script_version_pk> with an actual ScriptVersion pk
   # Replace <username> and <password> with your credentials
   curl -X DELETE \
     -u <username>:<password> \
     http://localhost:8000/api/scripts/<script_version_pk>/delete-all-versions/
   ```

3. **Expected responses**:
   - **Success (204)**: Script and all versions deleted
   - **404**: Script version not found
   - **403**: Permission denied (not the owner)
   - **401**: Authentication required

### Test Scenario 5: Verify Cascade Deletion

1. **Before deletion**, check the database:
   ```python
   # In Django shell: python manage.py shell
   from scripts.models import Script, ScriptVersion
   script = Script.objects.get(pk=<script_id>)
   version_count = script.versions.count()
   print(f"Script has {version_count} versions")
   ```

2. **Delete all versions** using either method

3. **After deletion**, verify:
   ```python
   # Script should be gone
   Script.objects.filter(pk=<script_id>).exists()  # Should be False
   
   # All versions should be gone
   ScriptVersion.objects.filter(script_id=<script_id>).exists()  # Should be False
   ```

## Automated Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov scripts

# Run specific test file
pytest tests/test_delete_all_versions.py -v
```

### Example Test File

See `tests/test_delete_all_versions.py` for a complete test suite.

