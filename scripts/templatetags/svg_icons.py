from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def svg_icon(icon_name):
    return format_html(
        '<svg class="bi bi-{0}" width="16" height="16" viewBox="0 0 16 16" '
        'fill="currentColor" aria-hidden="true" focusable="false">'
        '<use href="#bi-{0}"></use></svg>',
        icon_name,
    )
