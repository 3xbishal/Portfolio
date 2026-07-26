"""
Context processors for the custom admin panel.
"""

from .models import ContactMessage


def admin_context(request):
    """
    Provide admin-specific context variables.
    Only adds data when the user is authenticated (admin area).
    """
    if request.user.is_authenticated:
        return {
            'unread_count': ContactMessage.objects.filter(is_read=False).count(),
        }
    return {}
