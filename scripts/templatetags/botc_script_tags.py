from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def user_voted(context):
    user = context["user"]
    if user.is_authenticated:
        if user.votes.filter(script=context["record"]).exists():
            return True
    return False


@register.simple_tag(takes_context=True)
def user_favourite(context, script_version):
    user = context["user"]
    if user.is_authenticated:
        if user.favourites.filter(script=script_version).exists():
            return "star-fill"
    return "star"


@register.filter
def split(string):
    return string.split(" ")
