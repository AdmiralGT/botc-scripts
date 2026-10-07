from collections.abc import Iterable

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe

# A literal newline inside an HTML attribute value is collapsed to a space, so use the character reference.
HTML_NEWLINE = "&#10;"


def join_lines_for_html_attribute(lines: Iterable[str]) -> SafeString:
    """
    Escape each line and join them with an encoded newline so the result can be used inside an
    HTML attribute value, e.g. <meta content="...">.

    The lines can contain user supplied text (homebrew character names, unrecognised character ids),
    so every line is escaped before the result is marked safe. Without this a quote character in an
    uploaded script would end the attribute early and allow arbitrary markup to be injected.
    """
    return mark_safe(HTML_NEWLINE.join(escape(line) for line in lines))
