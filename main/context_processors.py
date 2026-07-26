"""
Context processors for the portfolio application.
Provides global context variables available in all templates.
"""

from .models import Profile


def profile_context(request):
    """
    Provide the active profile and global site data to all templates.
    """
    profile = Profile.objects.filter(is_active=True).first()
    return {
        'profile': profile,
        'site_name': f"{profile.name}'s Portfolio" if profile else 'My Portfolio',
    }
