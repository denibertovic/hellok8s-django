from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    """
    Adapter to control allauth new signups via DJANGO_ALLOW_REGISTRATION setting.
    """

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.
        Returns the value of DJANGO_ALLOW_REGISTRATION setting.
        """
        return settings.ALLOW_REGISTRATION
