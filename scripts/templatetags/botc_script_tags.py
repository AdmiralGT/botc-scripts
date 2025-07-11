from django import template
from scripts import models
from babel.core import Locale, UnknownLocaleError

register = template.Library()


@register.simple_tag(takes_context=True)
def user_voted(context, script_version):
    user = context["user"]
    if user.votes.filter(parent=script_version.script).exists():
        return "btn-danger"
    return "btn-success"


@register.simple_tag(takes_context=True)
def user_voted_icon(context, script_version):
    user = context["user"]
    if user.votes.filter(parent=script_version.script).exists():
        return "hand-thumbs-down-fill"
    return "hand-thumbs-up-fill"


@register.simple_tag(takes_context=True)
def user_favourite(context, script_version):
    user = context["user"]
    if user.favourites.filter(parent=script_version.script).exists():
        return "star-fill"
    return "star"


@register.simple_tag(takes_context=True)
def script_has_tag(context, tag, initial):
    tags = initial.get("tags", None)
    if tags and tag in tags:
        return True
    return False


@register.simple_tag()
def script_in_collection(collection, script_version):
    if script_version in collection.scripts.all():
        return True
    return False


@register.simple_tag()
def script_not_in_user_collection(user, script_version):
    for collection in user.collections.all():
        if script_version not in collection.scripts.all():
            return True
    return False


def get_colour_from_character_type(character_type):
    match character_type:
        case models.CharacterType.TOWNSFOLK:
            return "style=color:#0000ff"
        case models.CharacterType.OUTSIDER:
            return "style=color:#00ccff"
        case models.CharacterType.MINION:
            return "style=color:#ff8000"
        case models.CharacterType.DEMON:
            return "style=color:#ff0000"
        case models.CharacterType.TRAVELLER:
            return "style=color:#cc0099"
        case models.CharacterType.FABLED:
            return "style=color:#996600"
        case _:
            return "style=color:#000000"


@register.simple_tag()
def character_colourisation(character_id):
    try:
        character = models.ClocktowerCharacter.objects.get(character_id=character_id)
        return get_colour_from_character_type(character.character_type)
    except models.ClocktowerCharacter.DoesNotExist:
        try:
            character = models.HomebrewCharacter.objects.get(character_id=character_id)
            return get_colour_from_character_type(character.character_type)
        except models.HomebrewCharacter.DoesNotExist:
            return "style=color:#000000"


@register.simple_tag()
def character_type_change(content, counter):
    if counter > 0:
        prev_character_id = content[counter - 1].get("id", None)
        curr_character_id = content[counter].get("id", None)
        try:
            prev_character = models.ClocktowerCharacter.objects.get(character_id=prev_character_id)
        except models.ClocktowerCharacter.DoesNotExist:
            try:
                prev_character = models.HomebrewCharacter.objects.get(character_id=prev_character_id)
            except models.HomebrewCharacter.DoesNotExist:
                return False

        try:
            curr_character = models.ClocktowerCharacter.objects.get(character_id=curr_character_id)
        except models.ClocktowerCharacter.DoesNotExist:
            try:
                curr_character = models.HomebrewCharacter.objects.get(character_id=curr_character_id)
            except models.HomebrewCharacter.DoesNotExist:
                return False

        if prev_character and curr_character:
            if prev_character.character_type != curr_character.character_type:
                return True
    return False


@register.simple_tag()
def convert_id_to_friendly_text(character_id):
    try:
        return models.ClocktowerCharacter.objects.get(character_id=character_id).character_name
    except models.ClocktowerCharacter.DoesNotExist:
        try:
            return models.HomebrewCharacter.objects.get(character_id=character_id).character_name
        except models.HomebrewCharacter.DoesNotExist:
            return character_id


@register.filter
def split(string):
    return string.split(" ")


@register.simple_tag()
def active_tab_status(tab: str, active_tab: str):
    if tab in ["notes-tab", "characters-tab"]:
        if active_tab:
            return ""
        return "show active"
    if tab == active_tab:
        return "show active"
    return ""


@register.simple_tag()
def active_aria_status(aria: str, active_tab: str):
    if aria in ["notes-tab", "characters-tab"]:
        if active_tab:
            return ""
        return "active"
    if aria == active_tab:
        return "active"
    return ""


@register.simple_tag()
def get_language_name(locale: str):
    try:
        return Locale.parse(locale).display_name
    except UnknownLocaleError:
        if locale == "ja_JA":
            return get_language_name("ja_JP")
        elif locale == "kw_KW":
            return get_language_name("ar_KW")

        return locale


@register.simple_tag()
def get_character_percentage(count: int, total: int):
    percentage = count * 100 / total
    return f"{percentage:.2f}%"
