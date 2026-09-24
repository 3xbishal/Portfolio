"""
Custom template tags and filters for the portfolio application.
"""

import re

from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator

register = template.Library()

# Characters people commonly paste at the start of list lines (from Word, PDFs
# or CVs): bullets, middle dots, dashes, asterisks.
_BULLET_RE = re.compile(r'^\s*[•●▪◦·–—*-]\s*')


@register.filter
def mul(value, arg):
    """Multiply two numbers."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def split(value, delimiter=","):
    """Split a string by delimiter and return a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]


@register.filter
def summary(value, words=24):
    """Turn free-form text (often a bulleted list) into a short one-paragraph
    teaser for cards: drops bullet markers, ends each bullet item as a
    sentence, rejoins wrapped lines with spaces, then truncates to `words`."""
    text = strip_tags(value or '')
    parts = []
    for line in text.splitlines():
        is_item = bool(_BULLET_RE.match(line))
        line = _BULLET_RE.sub('', line).strip()
        if not line:
            continue
        if is_item and parts and parts[-1][-1] not in '.!?:;,':
            parts[-1] += '.'
        parts.append(line)
    try:
        words = int(words)
    except (TypeError, ValueError):
        words = 24
    text = ' '.join(parts)
    if len(text.split()) <= words:
        return text
    # Drop a trailing full stop/comma so the ellipsis doesn't read "word.…"
    return Truncator(text).words(words, truncate='').rstrip(' .,;:') + '…'


@register.filter
def strip(value):
    """Strip whitespace from a string."""
    if not value:
        return ""
    return value.strip()
