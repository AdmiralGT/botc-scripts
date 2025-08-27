"""
Tests for validators.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from scripts import models
from scripts.validators_enhanced import (
    validate_file_size,
    validate_json_file,
    validate_pdf_file,
    validate_script_name,
    validate_author_name,
    validate_version_string,
    validate_character_counts,
    validate_session_ids,
    validate_homebrew_character,
    validate_json,
    MAX_JSON_SIZE,
    MAX_PDF_SIZE,
)


class FileValidatorTest(TestCase):
    """Tests for file validators."""
    
    def test_validate_file_size_valid(self):
        """Test that valid file sizes pass."""
        file = SimpleUploadedFile("test.json", b"content")
        # Should not raise
        validate_file_size(file, 1024, "JSON")
        
    def test_validate_file_size_invalid(self):
        """Test that oversized files are rejected."""
        file = SimpleUploadedFile("test.json", b"x" * 1000)
        
        with self.assertRaises(ValidationError) as context:
            validate_file_size(file, 100, "JSON")
            
        self.assertIn("exceeds maximum", str(context.exception))
        
    def test_validate_json_file_valid(self):
        """Test valid JSON file."""
        content = b'[{"id": "imp"}]'
        file = SimpleUploadedFile("test.json", content)
        
        # Should not raise
        validate_json_file(file)
        
    def test_validate_json_file_invalid_json(self):
        """Test invalid JSON content."""
        file = SimpleUploadedFile("test.json", b"not json")
        
        with self.assertRaises(ValidationError) as context:
            validate_json_file(file)
            
        self.assertIn("Invalid JSON file", str(context.exception))
        
    def test_validate_pdf_file_valid(self):
        """Test valid PDF file."""
        # PDF files start with %PDF-
        content = b'%PDF-1.4\n%fake pdf content'
        file = SimpleUploadedFile("test.pdf", content)
        
        # Should not raise
        validate_pdf_file(file)
        
    def test_validate_pdf_file_invalid(self):
        """Test invalid PDF file."""
        file = SimpleUploadedFile("test.pdf", b"not a pdf")
        
        with self.assertRaises(ValidationError) as context:
            validate_pdf_file(file)
            
        self.assertIn("Invalid PDF file format", str(context.exception))


class StringValidatorTest(TestCase):
    """Tests for string validators."""
    
    def test_validate_script_name_valid(self):
        """Test valid script names."""
        validate_script_name("My Script")
        validate_script_name("Script-123")
        validate_script_name("A" * 100)  # Max length
        
    def test_validate_script_name_empty(self):
        """Test empty script name."""
        with self.assertRaises(ValidationError) as context:
            validate_script_name("")
            
        self.assertIn("required", str(context.exception))
        
    def test_validate_script_name_too_long(self):
        """Test overly long script name."""
        with self.assertRaises(ValidationError) as context:
            validate_script_name("A" * 101)
            
        self.assertIn("exceeds maximum length", str(context.exception))
        
    def test_validate_script_name_forbidden_chars(self):
        """Test script name with forbidden characters."""
        forbidden_names = [
            "Script/Name",
            "Script\\Name",
            "Script\nName",
            "Script\0Name",
        ]
        
        for name in forbidden_names:
            with self.assertRaises(ValidationError) as context:
                validate_script_name(name)
                
            self.assertIn("forbidden character", str(context.exception))
            
    def test_validate_author_name_valid(self):
        """Test valid author names."""
        validate_author_name("John Doe")
        validate_author_name(None)  # Optional
        validate_author_name("A" * 100)  # Max length
        
    def test_validate_author_name_too_long(self):
        """Test overly long author name."""
        with self.assertRaises(ValidationError) as context:
            validate_author_name("A" * 101)
            
        self.assertIn("exceeds maximum length", str(context.exception))
        
    def test_validate_version_string_valid(self):
        """Test valid version strings."""
        validate_version_string("1.0")
        validate_version_string("2.1.3")
        validate_version_string("1.0.0-beta")
        
    def test_validate_version_string_invalid(self):
        """Test invalid version strings."""
        invalid_versions = ["", "abc", "1.2.3.4.5.6.7"]
        
        for version in invalid_versions:
            with self.assertRaises(ValidationError) as context:
                validate_version_string(version)
                
            self.assertIn("Invalid version string", str(context.exception))


class CharacterValidatorTest(TestCase):
    """Tests for character validators."""
    
    def setUp(self):
        """Set up test data."""
        # Create some characters for testing
        models.ClocktowerCharacter.objects.create(
            character_id="imp",
            character_name="Imp",
            character_type=models.CharacterType.DEMON,
            edition=models.Edition.BASE,
            ability="Test"
        )
        
    def test_validate_character_counts_valid(self):
        """Test valid character composition."""
        content = [
            {"id": "washerwoman"},
            {"id": "imp"},
        ]
        
        # Should not raise
        validate_character_counts(content)
        
    def test_validate_character_counts_no_demon(self):
        """Test script without demon."""
        content = [
            {"id": "washerwoman"},
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_character_counts(content)
            
        self.assertIn("must contain at least one Demon", str(context.exception))
        
    def test_validate_homebrew_character_valid(self):
        """Test valid homebrew character."""
        script = models.Script.objects.create(name="Test")
        content = [
            {
                "id": "custom",
                "name": "Custom Character",
                "team": "townsfolk",
                "ability": "Does something"
            }
        ]
        
        # Should not raise
        validate_homebrew_character(content, script)
        
    def test_validate_homebrew_character_missing_fields(self):
        """Test homebrew character missing required fields."""
        script = models.Script.objects.create(name="Test")
        
        # Missing name
        content = [
            {
                "id": "custom",
                "team": "townsfolk",
            }
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_homebrew_character(content, script)
            
        self.assertIn("missing name", str(context.exception))
        
        # Missing team
        content = [
            {
                "id": "custom",
                "name": "Custom",
            }
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_homebrew_character(content, script)
            
        self.assertIn("missing team", str(context.exception))
        
    def test_validate_homebrew_character_invalid_team(self):
        """Test homebrew character with invalid team."""
        script = models.Script.objects.create(name="Test")
        content = [
            {
                "id": "custom",
                "name": "Custom",
                "team": "invalid_team",
            }
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_homebrew_character(content, script)
            
        self.assertIn("invalid team", str(context.exception))


class JSONValidatorTest(TestCase):
    """Tests for JSON content validators."""
    
    def test_validate_json_valid(self):
        """Test valid JSON content."""
        content = [
            {"id": "imp"},
            {"id": "washerwoman"},
        ]
        
        # Should not raise
        validate_json(content)
        
    def test_validate_json_not_list(self):
        """Test non-list JSON."""
        content = {"id": "imp"}
        
        with self.assertRaises(ValidationError) as context:
            validate_json(content)
            
        self.assertIn("must be a list", str(context.exception))
        
    def test_validate_json_empty(self):
        """Test empty JSON."""
        with self.assertRaises(ValidationError) as context:
            validate_json([])
            
        self.assertIn("cannot be empty", str(context.exception))
        
    def test_validate_json_too_many_characters(self):
        """Test JSON with too many characters."""
        content = [{"id": f"char{i}"} for i in range(101)]
        
        with self.assertRaises(ValidationError) as context:
            validate_json(content)
            
        self.assertIn("too many characters", str(context.exception))
        
    def test_validate_json_duplicate_ids(self):
        """Test JSON with duplicate character IDs."""
        content = [
            {"id": "imp"},
            {"id": "imp"},
        ]
        
        with self.assertRaises(ValidationError) as context:
            validate_json(content)
            
        self.assertIn("Duplicate character ID", str(context.exception))


class SessionValidatorTest(TestCase):
    """Tests for session data validators."""
    
    def test_validate_session_ids_valid(self):
        """Test valid session IDs."""
        ids = [1, 2, 3, 4, 5]
        result = validate_session_ids(ids)
        self.assertEqual(result, [1, 2, 3, 4, 5])
        
    def test_validate_session_ids_strings(self):
        """Test session IDs as strings (should convert)."""
        ids = ["1", "2", "3"]
        result = validate_session_ids(ids)
        self.assertEqual(result, [1, 2, 3])
        
    def test_validate_session_ids_invalid(self):
        """Test invalid session IDs."""
        # Not a list
        with self.assertRaises(ValidationError):
            validate_session_ids("not a list")
            
        # Contains non-numeric values
        with self.assertRaises(ValidationError):
            validate_session_ids([1, "abc", 3])
            
        # Contains negative values
        with self.assertRaises(ValidationError):
            validate_session_ids([1, -1, 3])
            
        # Contains None
        with self.assertRaises(ValidationError):
            validate_session_ids([1, None, 3])
