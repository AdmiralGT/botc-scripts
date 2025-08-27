"""
Service for character-related business logic.
"""
import logging
from typing import Dict, List, Optional
from django.db.models import QuerySet

from scripts import models, cache

logger = logging.getLogger(__name__)


class CharacterService:
    """Service class for character-related operations."""
    
    @staticmethod
    def translate_character(character_id: str, language: str) -> Dict:
        """
        Get translated character data.
        
        Args:
            character_id: ID of the character to translate
            language: Language code for translation
            
        Returns:
            Dictionary containing character data with translations
        """
        try:
            character = models.ClocktowerCharacter.objects.get(character_id=character_id)
        except models.ClocktowerCharacter.DoesNotExist:
            logger.warning(f"Character not found for translation: {character_id}")
            return {}
            
        original_character = character.full_character_json()
        
        try:
            translation = models.Translation.objects.get(
                character_id=character_id,
                language=language
            )
            translated_character = translation.full_character_json()
            # Merge original and translated data
            return {**original_character, **translated_character}
        except models.Translation.DoesNotExist:
            logger.info(f"No translation found for character {character_id} in language {language}")
            return original_character
    
    @staticmethod
    def translate_script_content(json_content: List[Dict], language: str) -> List[Dict]:
        """
        Translate all characters in a script.
        
        Args:
            json_content: List of character dictionaries
            language: Language code for translation
            
        Returns:
            List of translated character dictionaries
        """
        translated_content = []
        
        for character_data in json_content:
            if character_data.get("id") == "_meta":
                translated_content.append(character_data)
                continue
                
            character_id = character_data.get("id")
            if character_id:
                translated = CharacterService.translate_character(character_id, language)
                if translated:
                    translated_content.append(translated)
                else:
                    translated_content.append(character_data)
            else:
                translated_content.append(character_data)
                
        return translated_content
    
    @staticmethod
    def get_all_roles_for_edition(edition: models.Edition) -> List[Dict]:
        """
        Get all available roles for a specific edition.
        
        Args:
            edition: Edition enum value
            
        Returns:
            List of role dictionaries
        """
        import requests
        
        roles = []
        ordering = {}
        
        # Try to get SAO (Script Assistance Order) ordering
        try:
            response = requests.get(
                "https://botc-tools.vercel.app/sao-sorter/order.json",
                timeout=2
            )
            response.raise_for_status()
            ordering = response.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning(f"Failed to fetch SAO ordering: {e}")
        
        # Get characters for the edition
        characters = models.ClocktowerCharacter.objects.filter(
            edition__lte=edition
        ).values_list('character_id', flat=True)
        
        # Sort by SAO order if available, otherwise alphabetically
        sorted_chars = sorted(
            characters,
            key=lambda x: ordering.get(x, "7")
        )
        
        return [{"id": char_id} for char_id in sorted_chars]
    
    @staticmethod
    def count_character_in_scripts(
        character: models.ClocktowerCharacter,
        scripts: QuerySet
    ) -> int:
        """
        Count how many scripts contain a specific character.
        
        Args:
            character: Character to count
            scripts: QuerySet of scripts to search
            
        Returns:
            Number of scripts containing the character
        """
        return scripts.filter(
            content__contains=[{"id": character.character_id}]
        ).count()
    
    @staticmethod
    def get_character_statistics(
        scripts: QuerySet,
        character_type: Optional[models.CharacterType] = None,
        limit: int = 25
    ) -> List[tuple]:
        """
        Get statistics for character usage in scripts.
        
        Args:
            scripts: QuerySet of scripts to analyze
            character_type: Optional filter by character type
            limit: Maximum number of results to return
            
        Returns:
            List of (character, count) tuples
        """
        from collections import Counter
        
        character_count = Counter()
        
        # Filter characters by type if specified
        characters = models.ClocktowerCharacter.objects.all()
        if character_type:
            characters = characters.filter(character_type=character_type)
            
        # Count occurrences efficiently using database aggregation
        for character in characters:
            count = scripts.filter(
                content__contains=[{"id": character.character_id}]
            ).count()
            if count > 0:
                character_count[character] = count
                
        return character_count.most_common(limit)
    
    @staticmethod
    def validate_character_composition(script_content: List[Dict]) -> Dict[str, any]:
        """
        Validate the character composition of a script.
        
        Args:
            script_content: List of character dictionaries
            
        Returns:
            Dictionary with validation results and warnings
        """
        from scripts.services.script_service import ScriptService
        
        counts = ScriptService.count_characters_by_type(script_content)
        warnings = []
        
        # Check for minimum demon requirement
        if counts['demons'] < 1:
            warnings.append("Script must contain at least one Demon")
            
        # Check for reasonable character counts
        total_characters = sum(counts.values()) - counts['travellers'] - counts['fabled']
        
        if total_characters < 5:
            warnings.append("Script has very few characters (less than 5 non-Traveller/Fabled)")
        elif total_characters > 25:
            warnings.append("Script has many characters (more than 25 non-Traveller/Fabled)")
            
        # Check for balanced composition
        if counts['townsfolk'] == 0:
            warnings.append("No Townsfolk characters found")
            
        if counts['minions'] == 0:
            warnings.append("No Minion characters found")
            
        return {
            'counts': counts,
            'total': total_characters,
            'warnings': warnings,
            'is_valid': len(warnings) == 0
        }
