from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_user_voted(context):
    user = context["user"]
    if user.is_authenticated:
        if user.votes.filter(script=context["record"]).exists():
            return True
    return False


@register.simple_tag(takes_context=True)
def has_user_favourite(context):
    user = context["user"]
    if user.is_authenticated:
        if user.favourites.filter(script=context["script_version"]).exists():
            return True
    return False


@register.filter
def split(string):
    return string.split(" ")
