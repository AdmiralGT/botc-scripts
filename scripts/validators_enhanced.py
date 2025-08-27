"""
Enhanced validators for script data.
"""
import json as js
import logging
from typing import List, Dict, Any, Optional
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from versionfield import Version
import jsonschema
import requests

from scripts import models, constants

logger = logging.getLogger(__name__)

# File size limits
MAX_JSON_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB


def validate_file_size(file: UploadedFile, max_size: int, file_type: str) -> None:
    """
    Validate that an uploaded file doesn't exceed size limits.
    
    Args:
        file: The uploaded file
        max_size: Maximum allowed size in bytes
        file_type: Type of file for error message
        
    Raises:
        ValidationError: If file exceeds size limit
    """
    if file.size > max_size:
        raise ValidationError(
            f"{file_type} file size ({file.size} bytes) exceeds maximum "
            f"allowed size ({max_size} bytes)"
        )


def validate_json_file(json_file: UploadedFile) -> None:
    """
    Validate a JSON file upload.
    
    Args:
        json_file: The uploaded JSON file
        
    Raises:
        ValidationError: If file is invalid
    """
    validate_file_size(json_file, MAX_JSON_SIZE, "JSON")
    
    try:
        content = json_file.read()
        js.loads(content)
        json_file.seek(0)
    except js.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON file: {e}")
    except Exception as e:
        raise ValidationError(f"Error reading JSON file: {e}")


def validate_pdf_file(pdf_file: UploadedFile) -> None:
    """
    Validate a PDF file upload.
    
    Args:
        pdf_file: The uploaded PDF file
        
    Raises:
        ValidationError: If file is invalid
    """
    validate_file_size(pdf_file, MAX_PDF_SIZE, "PDF")
    
    # Check PDF header
    pdf_file.seek(0)
    header = pdf_file.read(5)
    pdf_file.seek(0)
    
    if header != b'%PDF-':
        raise ValidationError("Invalid PDF file format")


def validate_script_json_schema(json_content: List[Dict], schema_version: Optional[str] = None) -> None:
    """
    Validate script JSON against the official schema.
    
    Args:
        json_content: The script JSON content
        schema_version: Optional schema version to validate against
        
    Raises:
        ValidationError: If JSON doesn't match schema
    """
    import os
    
    if schema_version is None:
        schema_version = os.environ.get("JSON_SCHEMA_VERSION", "v3.45.0")
        
    schema_url = (
        f"https://raw.githubusercontent.com/ThePandemoniumInstitute/"
        f"botc-release/refs/tags/{schema_version}/script-schema.json"
    )
    
    try:
        response = requests.get(schema_url, timeout=5)
        response.raise_for_status()
        schema = response.json()
        
        # Allow additional properties on character objects
        if "items" in schema and "oneOf" in schema["items"]:
            if len(schema["items"]["oneOf"]) > 0:
                schema["items"]["oneOf"][0]["additionalProperties"] = True
                
        jsonschema.validate(json_content, schema)
        
    except requests.RequestException as e:
        logger.warning(f"Could not fetch JSON schema: {e}")
        # Don't fail validation if we can't fetch the schema
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(
            f"Script JSON does not conform to schema {schema_version}: {e.message}"
        )
    except jsonschema.exceptions.SchemaError as e:
        logger.error(f"Invalid schema: {e}")
        # Don't fail validation if the schema itself is invalid


def validate_character_counts(json_content: List[Dict]) -> None:
    """
    Validate that a script has reasonable character counts.
    
    Args:
        json_content: The script JSON content
        
    Raises:
        ValidationError: If character counts are invalid
    """
    from scripts.services.character_service import CharacterService
    
    validation = CharacterService.validate_character_composition(json_content)
    
    if not validation['is_valid']:
        raise ValidationError(
            f"Script composition issues: {'; '.join(validation['warnings'])}"
        )


def validate_version_string(version_str: str) -> None:
    """
    Validate a version string.
    
    Args:
        version_str: Version string to validate
        
    Raises:
        ValidationError: If version string is invalid
    """
    try:
        Version(version_str)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid version string '{version_str}': {e}")


def validate_script_name(name: str) -> None:
    """
    Validate a script name.
    
    Args:
        name: Script name to validate
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError("Script name is required")
        
    if len(name) > constants.MAX_SCRIPT_NAME_LENGTH:
        raise ValidationError(
            f"Script name exceeds maximum length of {constants.MAX_SCRIPT_NAME_LENGTH} characters"
        )
        
    # Check for problematic characters
    forbidden_chars = ['/', '\\', '\0', '\n', '\r', '\t']
    for char in forbidden_chars:
        if char in name:
            raise ValidationError(f"Script name contains forbidden character: {repr(char)}")


def validate_author_name(name: Optional[str]) -> None:
    """
    Validate an author name.
    
    Args:
        name: Author name to validate
        
    Raises:
        ValidationError: If name is invalid
    """
    if name and len(name) > constants.MAX_AUTHOR_NAME_LENGTH:
        raise ValidationError(
            f"Author name exceeds maximum length of {constants.MAX_AUTHOR_NAME_LENGTH} characters"
        )


def validate_homebrew_character(json_content: List[Dict], script: models.Script) -> None:
    """
    Validate homebrew character definitions.
    
    Args:
        json_content: Script JSON content
        script: Script model instance
        
    Raises:
        ValidationError: If homebrew characters are invalid
    """
    for item in json_content:
        if item.get("id") == "_meta":
            continue
            
        # Check if it's a homebrew character (has additional properties)
        if len(item.keys()) > 1:
            # Validate required homebrew fields
            if not item.get("name"):
                raise ValidationError(
                    f"Homebrew character {item.get('id', 'unknown')} missing name"
                )
                
            if not item.get("team"):
                raise ValidationError(
                    f"Homebrew character {item.get('id', 'unknown')} missing team"
                )
                
            # Validate team value
            valid_teams = ["townsfolk", "outsider", "minion", "demon", "traveller", "traveler", "fabled"]
            if item.get("team", "").lower() not in valid_teams:
                raise ValidationError(
                    f"Homebrew character {item.get('id', 'unknown')} has invalid team: {item.get('team')}"
                )


def validate_json(json_content: List[Dict]) -> None:
    """
    Comprehensive validation of script JSON content.
    
    Args:
        json_content: Script JSON content
        
    Raises:
        ValidationError: If JSON is invalid
    """
    if not isinstance(json_content, list):
        raise ValidationError("Script JSON must be a list of character objects")
        
    if len(json_content) == 0:
        raise ValidationError("Script JSON cannot be empty")
        
    if len(json_content) > 100:
        raise ValidationError("Script contains too many characters (maximum 100)")
        
    # Check for duplicate character IDs
    character_ids = []
    for item in json_content:
        if item.get("id") and item.get("id") != "_meta":
            if item["id"] in character_ids:
                raise ValidationError(f"Duplicate character ID: {item['id']}")
            character_ids.append(item["id"])
            
    # Validate character counts
    validate_character_counts(json_content)


def valid_version(value: str) -> None:
    """
    Django validator for version fields.
    
    Args:
        value: Version string to validate
        
    Raises:
        ValidationError: If version is invalid
    """
    validate_version_string(value)


def validate_session_ids(ids: List[Any]) -> List[int]:
    """
    Validate and sanitize a list of IDs from session data.
    
    Args:
        ids: List of potential IDs
        
    Returns:
        List of validated integer IDs
        
    Raises:
        ValidationError: If IDs are invalid
    """
    if not isinstance(ids, list):
        raise ValidationError("Invalid session data: expected list")
        
    validated_ids = []
    for id_val in ids:
        try:
            # Ensure it's an integer
            validated_id = int(id_val)
            if validated_id < 0:
                raise ValidationError(f"Invalid ID: {id_val}")
            validated_ids.append(validated_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid ID in session: {id_val}")
            
    return validated_ids
