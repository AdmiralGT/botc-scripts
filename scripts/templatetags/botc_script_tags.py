from django import template
from scripts import models
from babel.core import Locale, UnknownLocaleError

register = template.Library()


@register.simple_tag(takes_context=True)
def user_voted(context, script_version):
    user = context["user"]
    if user.votes.filter(script=script_version).exists():
        return "btn-danger"
    return "btn-primary"


@register.simple_tag(takes_context=True)
def user_favourite(context, script_version):
    user = context["user"]
    if user.favourites.filter(script=script_version).exists():
        return "star-fill"
    return "star"


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


@register.simple_tag()
def character_colourisation(character_id):
    try:
        character = models.Character.objects.get(character_id=character_id)
        if character.character_type == models.CharacterType.TOWNSFOLK:
            return "style=color:#0000ff"
        if character.character_type == models.CharacterType.OUTSIDER:
            return "style=color:#00ccff"
        if character.character_type == models.CharacterType.MINION:
            return "style=color:#ff8000"
        if character.character_type == models.CharacterType.DEMON:
            return "style=color:#ff0000"
        if character.character_type == models.CharacterType.TRAVELLER:
            return "style=color:#cc0099"
        if character.character_type == models.CharacterType.FABLED:
            return "style=color:#996600"
    except models.Character.DoesNotExist:
        return "style=color:#000000"


@register.simple_tag()
def character_type_change(content, counter):
    if counter > 0:
        prev_character_id = content[counter - 1]["id"]
        curr_character_id = content[counter]["id"]
        try:
            prev_character = models.Character.objects.get(
                character_id=prev_character_id
            )
            curr_character = models.Character.objects.get(
                character_id=curr_character_id
            )
        except models.Character.DoesNotExist:
            return False

        if prev_character and curr_character:
            if prev_character.character_type != curr_character.character_type:
                return True
    return False


@register.simple_tag()
def convert_id_to_friendly_text(character_id):
    try:
        return models.Character.objects.get(character_id=character_id).character_name
    except models.Character.DoesNotExist:
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
