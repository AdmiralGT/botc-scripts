import time
import uuid

from django.core.cache import cache

from scripts import models

CACHE_TIMEOUT = 60 * 60 * 1  # 1 hour
ADVANCED_SEARCH_TIMEOUT = 300  # 5 minutes
CLOCKTOWER_CHARACTERS_CACHE_KEY = "clocktower_characters"
HOMEBREW_CHARACTERS_CACHE_KEY = "homebrew_characters"

# Unpickling ~200 model instances from the cache backend is far more expensive than a dictionary
# lookup, and the template tags look characters up many times per page. A short-lived in-process
# copy keeps those lookups cheap while still picking up changes quickly.
LOCAL_TIMEOUT = 60
_local_copies: dict[str, tuple[dict, float]] = {}


def _get_character_map(model, cache_key: str, force: bool) -> dict:
    now = time.monotonic()
    local = _local_copies.get(cache_key)
    if not force and local is not None and local[1] > now:
        return local[0]

    characters = None if force else cache.get(cache_key)
    if characters is None:
        characters = {character.character_id: character for character in model.objects.all()}
        cache.set(cache_key, characters, timeout=CACHE_TIMEOUT)

    _local_copies[cache_key] = (characters, now + LOCAL_TIMEOUT)
    return characters


def get_clocktower_characters(force=False) -> dict[str, models.ClocktowerCharacter]:
    return _get_character_map(models.ClocktowerCharacter, CLOCKTOWER_CHARACTERS_CACHE_KEY, force)


def get_homebrew_characters(force=False) -> dict[str, models.HomebrewCharacter]:
    return _get_character_map(models.HomebrewCharacter, HOMEBREW_CHARACTERS_CACHE_KEY, force)


def get_character(character_id: str) -> models.ClocktowerCharacter | models.HomebrewCharacter | None:
    """
    Look up a character by ID, preferring official characters over homebrew ones.
    """
    return get_clocktower_characters().get(character_id) or get_homebrew_characters().get(character_id)


def store_advanced_search_results(pk_list: list[int]) -> str:
    cache_key = uuid.uuid4().hex
    cache.set(cache_key, {"queryset_pks": pk_list, "num_results": len(pk_list)}, timeout=ADVANCED_SEARCH_TIMEOUT)
    return cache_key


def get_advanced_search_results(cache_key: str) -> dict | None:
    return cache.get(cache_key)
