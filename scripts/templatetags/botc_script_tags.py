from django import template
from scripts import characters

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
def character_colourisation(character):
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.TOWNSFOLK
    ):
        return "color:#0000FF"
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.OUTSIDER
    ):
        return "color:#0080FF"
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.MINION
    ):
        return "color:#FF4040"
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.DEMON
    ):
        return "color:#A00000"
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.TRAVELLER
    ):
        return "color:#FF80FF"
    if (
        characters.Character.get(character).character_type
        == characters.CharacterType.FABLED
    ):
        return "color:#FFC400"


@register.filter
def split(string):
    return string.split(" ")
