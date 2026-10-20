"""
Business logic shared by the HTML views, the REST API and the management commands.
"""

from collections import Counter

import requests
from django.core.cache import cache as default_cache
from django.db import transaction
from versionfield import Version

from scripts import cache, models
from scripts.script_json import META_ID

SCRIPT_TOOL_ROLES_URL = "https://script.bloodontheclocktower.com/data/roles.json"
SAO_ORDER_URL = "https://botc-tools.vercel.app/sao-sorter/order.json"
EXTERNAL_REQUEST_TIMEOUT = 2  # seconds
DEFAULT_SAO_ORDER = "7"

OFFICIAL_ROLE_IDS_CACHE_KEY = "official_role_ids"
SAO_ORDER_CACHE_KEY = "sao_order"
EXTERNAL_DATA_CACHE_TIMEOUT = 60 * 60
EXTERNAL_FAILURE_CACHE_TIMEOUT = 60 * 5  # Don't hammer an external site that is down

COUNT_FIELD_BY_TYPE = {
    models.CharacterType.TOWNSFOLK: "num_townsfolk",
    models.CharacterType.OUTSIDER: "num_outsiders",
    models.CharacterType.MINION: "num_minions",
    models.CharacterType.DEMON: "num_demons",
    models.CharacterType.FABLED: "num_fabled",
    models.CharacterType.LORIC: "num_loric",
    models.CharacterType.TRAVELLER: "num_travellers",
}

# The "team" values that script JSON can contain. "traveler" is the spelling the official tools use.
CHARACTER_TYPE_BY_TEAM = {
    "townsfolk": models.CharacterType.TOWNSFOLK,
    "outsider": models.CharacterType.OUTSIDER,
    "minion": models.CharacterType.MINION,
    "demon": models.CharacterType.DEMON,
    "traveler": models.CharacterType.TRAVELLER,
    "traveller": models.CharacterType.TRAVELLER,
    "fabled": models.CharacterType.FABLED,
    "loric": models.CharacterType.LORIC,
}

HOMEBREWINESS_TAG_NAMES = {
    models.Homebrewiness.HYBRID: "Hybrid Script",
    models.Homebrewiness.HOMEBREW: "Homebrew Script",
}


def get_character_type_from_team(team: str | None) -> models.CharacterType:
    if not isinstance(team, str):
        return models.CharacterType.UNKNOWN
    return CHARACTER_TYPE_BY_TEAM.get(team, models.CharacterType.UNKNOWN)


def _fetch_json(url: str):
    """
    The decoded JSON at ``url``, or None if it couldn't be fetched.
    """
    try:
        response = requests.get(url, timeout=EXTERNAL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def get_official_role_ids() -> set[str]:
    """
    The IDs of the roles the official script tool knows about. This can include characters that have just
    been released and haven't been added to our database yet.
    """
    role_ids = default_cache.get(OFFICIAL_ROLE_IDS_CACHE_KEY)
    if role_ids is None:
        roles = _fetch_json(SCRIPT_TOOL_ROLES_URL)
        role_ids = {role["id"] for role in roles if isinstance(role, dict) and "id" in role} if roles else set()
        timeout = EXTERNAL_DATA_CACHE_TIMEOUT if role_ids else EXTERNAL_FAILURE_CACHE_TIMEOUT
        default_cache.set(OFFICIAL_ROLE_IDS_CACHE_KEY, role_ids, timeout=timeout)
    return role_ids


def get_sao_ordering() -> dict[str, str]:
    """
    The community "Storyteller Approved Order" of characters, keyed by character ID.
    """
    ordering = default_cache.get(SAO_ORDER_CACHE_KEY)
    if ordering is None:
        fetched = _fetch_json(SAO_ORDER_URL)
        ordering = fetched if isinstance(fetched, dict) else {}
        timeout = EXTERNAL_DATA_CACHE_TIMEOUT if ordering else EXTERNAL_FAILURE_CACHE_TIMEOUT
        default_cache.set(SAO_ORDER_CACHE_KEY, ordering, timeout=timeout)
    return ordering


def get_all_roles(edition: models.Edition) -> list[dict[str, str]]:
    """
    Every official character up to and including ``edition``, in Storyteller Approved Order.
    """
    ordering = get_sao_ordering()
    character_ids = (
        models.ClocktowerCharacter.objects.filter(edition__lte=edition)
        .order_by("character_id")
        .values_list("character_id", flat=True)
    )
    ordered_ids = sorted(character_ids, key=lambda character_id: ordering.get(character_id, DEFAULT_SAO_ORDER))
    return [{"id": character_id} for character_id in ordered_ids]


def _find_character(entry, official: dict, homebrew: dict):
    """
    The character a script entry refers to, or None if it is the _meta entry or isn't recognised.

    Entries are normally {"id": ...} objects, but plain ID strings are supported for legacy content
    (which can only refer to official characters).
    """
    if isinstance(entry, str):
        return official.get(entry)
    if isinstance(entry, dict):
        character_id = entry.get("id", "")
        if character_id == META_ID:
            return None
        return official.get(character_id) or homebrew.get(character_id)
    return None


def count_characters_by_type(script_content: list, homebrew_characters: dict | None = None) -> Counter:
    """
    Count the characters of each CharacterType in a script.

    ``homebrew_characters`` (keyed by character ID) can be provided when the cached homebrew characters might be
    out of date, e.g. straight after saving a script that introduced new ones.
    """
    official = cache.get_clocktower_characters()
    homebrew = cache.get_homebrew_characters() if homebrew_characters is None else homebrew_characters

    counts = Counter()
    for entry in script_content:
        character = _find_character(entry, official, homebrew)
        if character:
            counts[character.character_type] += 1
    return counts


def count_character(script_content: list, character_type: models.CharacterType) -> int:
    """
    Count the characters of a single type in a script. To count several types, use count_characters_by_type.
    """
    return count_characters_by_type(script_content)[character_type]


def get_character_count_fields(script_content: list, homebrew_characters: dict | None = None) -> dict[str, int]:
    """
    The ScriptVersion ``num_*`` fields for a script's content.
    """
    counts = count_characters_by_type(script_content, homebrew_characters)
    return {field: counts[character_type] for character_type, field in COUNT_FIELD_BY_TYPE.items()}


def calculate_edition(script_content: list) -> int:
    """
    The earliest edition that contains every character in the script. If we don't recognise a character it
    needs tokens we don't know about, so the script is treated as needing all of them.
    """
    official = cache.get_clocktower_characters()
    edition = models.Edition.BASE
    for entry in script_content:
        if isinstance(entry, dict) and entry.get("id", "") == META_ID:
            continue

        character = _find_character(entry, official, {})
        if character is None:
            return models.Edition.ALL
        edition = max(edition, character.edition)
    return edition


def _homebrew_character_fields(item: dict, script: models.Script) -> dict:
    image_url = item.get("image")
    if isinstance(image_url, list):
        image_url = ",".join(image_url)

    return {
        "script": script,
        "character_name": item.get("name"),
        "image_url": image_url,
        "character_type": get_character_type_from_team(item.get("team")).value,
        "ability": item.get("ability"),
        "first_night_position": item.get("firstNight"),
        "other_night_position": item.get("otherNight"),
        "first_night_reminder": item.get("firstNightReminder"),
        "other_night_reminder": item.get("otherNightReminder"),
        "global_reminders": ",".join(item.get("remindersGlobal", [])),
        "reminders": ",".join(item.get("reminders", [])),
        "modifies_setup": item.get("setup", False),
    }


def create_characters_and_determine_homebrew_status(
    script_content: list[dict], script: models.Script
) -> models.Homebrewiness:
    """
    Save any homebrew characters in the script, and work out whether the script is made up of official
    characters, homebrew characters or a mixture of both.
    """
    entries = [item for item in script_content if item.get("id", "") != META_ID]
    official_characters = models.ClocktowerCharacter.objects.in_bulk([item.get("id", "") for item in entries])

    # Ignore the _meta entry, and official Loric and Fabled characters, as they shouldn't count against
    # homebrew/hybrid status (homebrew Loric/Fabled characters still count).
    entries_to_ignore = len(script_content) - len(entries)
    non_clocktower_characters = 0
    official_role_ids = None

    for item in entries:
        character_id = item.get("id", "")

        official_character = official_characters.get(character_id)
        if official_character:
            if official_character.character_type in (models.CharacterType.LORIC, models.CharacterType.FABLED):
                entries_to_ignore += 1
            continue

        # It's possible we don't know about this character because it has just been released and it's not been
        # added to the database. In this case check the script tool for roles and if it's present, don't mark
        # this as a homebrew character.
        if official_role_ids is None:
            official_role_ids = get_official_role_ids()
        if character_id in official_role_ids:
            continue

        # If the character element has more than 1 key then it is almost certainly an attempt at a
        # homebrew/hybrid character, otherwise it's probably official.
        if len(item) == 1:
            continue

        non_clocktower_characters += 1
        models.HomebrewCharacter.objects.update_or_create(
            character_id=character_id, defaults=_homebrew_character_fields(item, script)
        )

    if non_clocktower_characters == len(script_content) - entries_to_ignore:
        return models.Homebrewiness.HOMEBREW
    if non_clocktower_characters > 0:
        return models.Homebrewiness.HYBRID
    return models.Homebrewiness.CLOCKTOWER


def supersede_latest_version(script: models.Script, new_version: str) -> tuple[bool, models.ScriptVersion | None]:
    """
    Mark the script's current latest version as no longer the latest if ``new_version`` is newer than it.

    Returns whether the new version will be the latest, and the version that was superseded (if any).
    """
    latest_version = script.latest_version()
    if latest_version is None:
        return True, None

    if Version(new_version) > latest_version.version:
        latest_version.latest = False
        latest_version.save(update_fields=["latest"])
        return True, latest_version

    # We're uploading an older version than the latest, so that's still the current latest.
    return False, None


def create_script_version(
    *,
    script: models.Script,
    content: list[dict],
    version: str,
    script_type: str,
    author: str | None,
    pdf,
    notes: str | None,
    is_latest: bool,
    tags=(),
    inherited_tags=(),
) -> models.ScriptVersion:
    """
    Create a new version of a script, working out its edition, character counts and homebrew status.
    """
    with transaction.atomic():
        homebrewiness = create_characters_and_determine_homebrew_status(content, script)

        # The character cache may not know about homebrew characters that were only just created, so look
        # them up directly.
        homebrew_characters = models.HomebrewCharacter.objects.in_bulk(
            [item.get("id", "") for item in content if item.get("id", "") != META_ID]
        )

        script_version = models.ScriptVersion.plain_objects.create(
            script=script,
            version=version,
            script_type=script_type,
            content=content,
            pdf=pdf,
            author=author,
            notes=notes or "",
            latest=is_latest,
            edition=calculate_edition(content),
            homebrewiness=homebrewiness,
            **get_character_count_fields(content, homebrew_characters),
        )

        homebrewiness_tag = get_homebrewiness_tag(homebrewiness)
        script_version.tags.add(*tags, *inherited_tags, *([homebrewiness_tag] if homebrewiness_tag else []))
    return script_version


def get_homebrewiness_tag(homebrewiness: models.Homebrewiness) -> models.ScriptTag | None:
    tag_name = HOMEBREWINESS_TAG_NAMES.get(homebrewiness)
    if tag_name is None:
        return None
    return models.ScriptTag.objects.filter(name=tag_name).first()


def delete_script_version(script_version: models.ScriptVersion) -> bool:
    """
    Delete a script version. The highest remaining version becomes the latest, and the script itself is
    deleted if that was its only version.

    Returns whether the script still exists.
    """
    script = script_version.script
    with transaction.atomic():
        script_version.delete()

        new_latest_version = script.latest_version()
        if new_latest_version is None:
            script.delete()
            return False

        if not new_latest_version.latest:
            new_latest_version.latest = True
            new_latest_version.save(update_fields=["latest"])
    return True


def translate_json_content(script_content: list[dict], language: str) -> list[dict]:
    """
    Replace each character in the script with its full character JSON translated into ``language``.

    Characters that aren't official characters can't be translated and are replaced with an empty object.
    The _meta entry is left as it is.
    """
    character_ids = [entry.get("id") for entry in script_content if entry.get("id") != META_ID]
    characters = models.ClocktowerCharacter.objects.in_bulk(character_ids)
    translations = {
        translation.character_id: translation
        for translation in models.Translation.objects.filter(language=language, character_id__in=character_ids)
    }

    translated_content = []
    for entry in script_content:
        character_id = entry.get("id")
        if character_id == META_ID:
            translated_content.append(entry)
            continue

        character = characters.get(character_id)
        if character is None:
            translated_content.append({})
            continue

        character_json = character.full_character_json()
        translation = translations.get(character_id)
        if translation is not None:
            character_json.update(translation.full_character_json())
        translated_content.append(character_json)
    return translated_content
