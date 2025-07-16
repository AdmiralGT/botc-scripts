from django.core.cache import cache
from scripts import models

CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours
CLOCKTOWER_CHARACTERS_CACHE_KEY = "clocktower_characters"
HOMEBREW_CHARACTERS_CACHE_KEY = "homebrew_characters"


def get_clocktower_characters(force=False) -> dict[str, models.ClocktowerCharacter]:
    characters = cache.get(CLOCKTOWER_CHARACTERS_CACHE_KEY)
    if force or characters is None:
        characters = {character.character_id: character for character in models.ClocktowerCharacter.objects.all()}
        cache.set(CLOCKTOWER_CHARACTERS_CACHE_KEY, characters, timeout=CACHE_TIMEOUT)  # Cache for 24 hours
    return characters


def get_homebrew_characters(force=False) -> dict[str, models.HomebrewCharacter]:
    characters = cache.get(HOMEBREW_CHARACTERS_CACHE_KEY)
    if force or characters is None:
        characters = {character.character_id: character for character in models.HomebrewCharacter.objects.all()}
        cache.set(HOMEBREW_CHARACTERS_CACHE_KEY, characters, timeout=CACHE_TIMEOUT)  # Cache for 24 hours
    return characters
