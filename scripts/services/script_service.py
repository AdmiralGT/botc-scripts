"""
Service for script-related business logic.
"""
import json as js
import logging
from typing import Dict, List, Tuple, Optional, Any
import requests
from django.db import transaction
from django.core.exceptions import ValidationError

from scripts import models, cache, constants

logger = logging.getLogger(__name__)


class ScriptService:
    """Service class for script-related operations."""
    
    @staticmethod
    def count_characters_by_type(script_content: List[Dict]) -> Dict[str, int]:
        """
        Count characters by type in a script.
        
        Args:
            script_content: List of character dictionaries
            
        Returns:
            Dictionary mapping character type to count
        """
        counts = {
            'townsfolk': 0,
            'outsiders': 0,
            'minions': 0,
            'demons': 0,
            'travellers': 0,
            'fabled': 0,
        }
        
        type_mapping = {
            models.CharacterType.TOWNSFOLK: 'townsfolk',
            models.CharacterType.OUTSIDER: 'outsiders',
            models.CharacterType.MINION: 'minions',
            models.CharacterType.DEMON: 'demons',
            models.CharacterType.TRAVELLER: 'travellers',
            models.CharacterType.FABLED: 'fabled',
        }
        
        clocktower_characters = cache.get_clocktower_characters()
        homebrew_characters = cache.get_homebrew_characters()
        
        for json_entry in script_content:
            if isinstance(json_entry, dict) and json_entry.get("id") == "_meta":
                continue
                
            character_id = json_entry.get("id") if isinstance(json_entry, dict) else json_entry
            character = clocktower_characters.get(character_id) or homebrew_characters.get(character_id)
            
            if character and character.character_type in type_mapping:
                counts[type_mapping[character.character_type]] += 1
        
        return counts
    
    @staticmethod
    def calculate_edition(script_content: List[Dict]) -> int:
        """
        Calculate the required edition for a script based on its characters.
        
        Args:
            script_content: List of character dictionaries
            
        Returns:
            Edition constant
        """
        edition = models.Edition.BASE
        clocktower_characters = cache.get_clocktower_characters()
        
        for json_entry in script_content:
            if isinstance(json_entry, dict) and json_entry.get("id") == "_meta":
                continue
                
            character_id = json_entry.get("id") if isinstance(json_entry, dict) else json_entry
            character = clocktower_characters.get(character_id)
            
            if not character:
                # Unknown character, requires ALL edition
                return models.Edition.ALL
            elif character.edition > edition:
                edition = character.edition
                
            if edition == models.Edition.ALL:
                return edition
                
        return edition
    
    @staticmethod
    def get_character_type_from_team(team: str) -> models.CharacterType:
        """
        Convert team string to CharacterType enum.
        
        Args:
            team: Team string from JSON
            
        Returns:
            CharacterType enum value
        """
        mapping = {
            "townsfolk": models.CharacterType.TOWNSFOLK,
            "outsider": models.CharacterType.OUTSIDER,
            "minion": models.CharacterType.MINION,
            "demon": models.CharacterType.DEMON,
            "traveler": models.CharacterType.TRAVELLER,
            "traveller": models.CharacterType.TRAVELLER,
            "fabled": models.CharacterType.FABLED,
        }
        return mapping.get(team.lower(), models.CharacterType.UNKNOWN)
    
    @staticmethod
    def fetch_official_roles(timeout: int = 2) -> Optional[List[Dict]]:
        """
        Fetch official roles from the Blood on the Clocktower API.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            List of role dictionaries or None if fetch fails
        """
        try:
            response = requests.get(
                "https://script.bloodontheclocktower.com/data/roles.json",
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, js.JSONDecodeError) as e:
            logger.warning(f"Failed to fetch official roles: {e}")
            return None
    
    @staticmethod
    def is_character_official(character_id: str, official_roles: Optional[List[Dict]] = None) -> bool:
        """
        Check if a character is an official Blood on the Clocktower character.
        
        Args:
            character_id: Character ID to check
            official_roles: Optional pre-fetched list of official roles
            
        Returns:
            True if character is official, False otherwise
        """
        if official_roles is None:
            official_roles = ScriptService.fetch_official_roles() or []
            
        return any(role.get("id") == character_id for role in official_roles)
    
    @classmethod
    @transaction.atomic
    def create_or_update_homebrew_characters(
        cls,
        script_content: List[Dict],
        script: models.Script
    ) -> models.Homebrewiness:
        """
        Create or update homebrew characters for a script and determine homebrew status.
        
        Args:
            script_content: List of character dictionaries
            script: Script model instance
            
        Returns:
            Homebrewiness level of the script
        """
        non_clocktower_characters = 0
        entries_to_ignore = 0
        official_roles = cls.fetch_official_roles()
        
        for item in script_content:
            if item.get("id", "") == "_meta":
                entries_to_ignore += 1
                continue
                
            # Check if it's the bootlegger character (special case)
            if item.get("id") == "bootlegger":
                entries_to_ignore += 1
                continue
                
            try:
                models.ClocktowerCharacter.objects.get(character_id=item.get("id", ""))
            except models.ClocktowerCharacter.DoesNotExist:
                # Check if it's a newly released official character
                if len(item.keys()) == 1 and official_roles:
                    if cls.is_character_official(item.get("id", ""), official_roles):
                        continue
                        
                non_clocktower_characters += 1
                cls._create_or_update_homebrew_character(item, script)
        
        # Determine homebrewiness
        total_characters = len(script_content) - entries_to_ignore
        if non_clocktower_characters == total_characters and total_characters > 0:
            return models.Homebrewiness.HOMEBREW
        elif non_clocktower_characters > 0:
            return models.Homebrewiness.HYBRID
        else:
            return models.Homebrewiness.CLOCKTOWER
    
    @staticmethod
    def _create_or_update_homebrew_character(item: Dict, script: models.Script) -> None:
        """
        Create or update a single homebrew character.
        
        Args:
            item: Character data dictionary
            script: Script model instance
        """
        image_url = item.get("image", "")
        if isinstance(image_url, list):
            image_url = ",".join(image_url)
            
        character_data = {
            "character_name": item.get("name", "Unknown"),
            "image_url": image_url,
            "character_type": ScriptService.get_character_type_from_team(
                item.get("team", "")
            ).value,
            "ability": item.get("ability", ""),
            "first_night_position": item.get("firstNight"),
            "other_night_position": item.get("otherNight"),
            "first_night_reminder": item.get("firstNightReminder"),
            "other_night_reminder": item.get("otherNightReminder"),
            "global_reminders": ",".join(item.get("remindersGlobal", [])),
            "reminders": ",".join(item.get("reminders", [])),
            "modifies_setup": item.get("setup", False),
        }
        
        try:
            homebrew_char = models.HomebrewCharacter.objects.get(
                character_id=item.get("id")
            )
            # Only update if it's the same script or has no script
            if not homebrew_char.script or homebrew_char.script == script:
                character_data["script"] = script
                models.HomebrewCharacter.objects.update_or_create(
                    character_id=item.get("id"),
                    defaults=character_data
                )
        except models.HomebrewCharacter.DoesNotExist:
            character_data["script"] = script
            models.HomebrewCharacter.objects.create(
                character_id=item.get("id"),
                **character_data
            )
    
    @staticmethod
    @transaction.atomic
    def update_script_tags(
        script_version: models.ScriptVersion,
        tags: List[models.ScriptTag],
        user,
        previous_version_tags=None
    ) -> None:
        """
        Update tags for a script version.
        
        Args:
            script_version: ScriptVersion instance
            tags: List of ScriptTag instances to set
            user: User making the update
            previous_version_tags: Optional tags from previous version
        """
        if user.is_staff:
            # Staff can see all tags, so apply their changes directly
            script_version.tags.set(tags)
        else:
            # Non-staff can't see non-public tags, preserve them
            current_non_public = script_version.tags.filter(public=False)
            script_version.tags.set(tags | current_non_public)
            
        # Handle inheritable tags from previous version
        if previous_version_tags:
            for tag in previous_version_tags.all():
                if tag.public and tag not in tags and not tag.inheritable:
                    # Remove non-inheritable public tags not in the new set
                    continue
                elif tag.inheritable and tag not in tags:
                    # Keep inheritable tags unless explicitly removed
                    script_version.tags.add(tag)
    
    @staticmethod
    def calculate_similarity(
        script1_content: List[Dict],
        script2_content: List[Dict],
        same_type: bool = True
    ) -> float:
        """
        Calculate similarity percentage between two scripts.
        
        Args:
            script1_content: Content of first script
            script2_content: Content of second script
            same_type: Whether the scripts are of the same type
            
        Returns:
            Similarity percentage (0-100)
        """
        # Filter out metadata entries
        chars1 = [c for c in script1_content if c.get("id") != "_meta"]
        chars2 = [c for c in script2_content if c.get("id") != "_meta"]
        
        if not chars1 or not chars2:
            return 0.0
            
        # Count matching characters
        chars1_ids = {c.get("id") for c in chars1 if c.get("id")}
        chars2_ids = {c.get("id") for c in chars2 if c.get("id")}
        matching = len(chars1_ids & chars2_ids)
        
        # Calculate similarity based on type
        if same_type:
            max_chars = max(len(chars1_ids), len(chars2_ids))
        else:
            min_chars = min(len(chars1_ids), len(chars2_ids))
            max_chars = max(min_chars, constants.STANDARD_TEENSYVILLE_CHARACTER_COUNT)
            
        if max_chars == 0:
            return 0.0
            
        return round((matching / max_chars) * 100, 2)
