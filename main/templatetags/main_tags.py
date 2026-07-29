"""
Custom template tags and filters for the portfolio application.
"""

from django import template

register = template.Library()


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
def strip(value):
    """Strip whitespace from a string."""
    if not value:
        return ""
    return value.strip()
