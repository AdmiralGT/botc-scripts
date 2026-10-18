import uuid

import requests
from django.core.cache import cache

from scripts import models

CACHE_TIMEOUT = 60 * 60 * 1  # 1 hour
CLOCKTOWER_CHARACTERS_CACHE_KEY = "clocktower_characters"
HOMEBREW_CHARACTERS_CACHE_KEY = "homebrew_characters"
OFFICIAL_ROLES_CACHE_KEY = "official_roles"


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


def store_advanced_search_results(pk_list: list[int]) -> str:
    cache_key = f"{uuid.uuid4().hex}"
    cache.set(cache_key, {"queryset_pks": pk_list, "num_results": len(pk_list)}, timeout=300)
    return cache_key


def get_advanced_search_results(cache_key: str) -> dict | None:
    return cache.get(cache_key)


def get_official_roles() -> list[dict] | None:
    roles = cache.get(OFFICIAL_ROLES_CACHE_KEY)
    if roles is not None:
        return roles

    try:
        response = requests.get("https://release.botc.app/resources/data/roles.json", timeout=2)
    except requests.exceptions.Timeout:
        return None

    if not response.ok:
        return None

    roles = response.json()
    cache.set(OFFICIAL_ROLES_CACHE_KEY, roles, timeout=CACHE_TIMEOUT)
    return roles
