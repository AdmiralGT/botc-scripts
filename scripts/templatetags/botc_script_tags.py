from django import template

register = template.Library()


@register.simple_tag()
def get_tag_type(value):
    if value.pk == 1:
        return "badge-secondary"
    elif value.pk == 2:
        return "badge-info"
    return "badge-primary"


@register.simple_tag(takes_context=True)
def has_user_voted(context):
    user = context["user"]
    if user.votes.filter(script=context["record"]).exists():
        return True
    return False
