from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import six
from django.utils.translation import ugettext as _
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthAlreadyAssociated

from collections import OrderedDict

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.profile.email_confirmed)
        )

account_activation_token = AccountActivationTokenGenerator()

class SteamAuthAuthAlreadyAssociatedMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            messages.error(request, _('Error: Steam Account already associated with another user!'))
            return redirect('portal:profile')
        else:
            raise exception

def social_links(request):
    SHOW_SPONSORS = settings.SHOW_SPONSORS
    social = [
        ('facebook', 'https://www.facebook.com/FragFestIIITA/'),
        ('twitter', 'https://twitter.com/FragFestIIITA/'),
        ('youtube-play', 'https://www.youtube.com/channel/UCsuoNyw1L8W58mXAsXZ90ZA'),
        ('google-plus', 'https://plus.google.com/+FragFest'),
        ('twitch', 'https://www.twitch.tv/FragFestIIITA/'),
        ('steam', 'https://steamcommunity.com/groups/Frag-Fest')
    ]
    social = OrderedDict(social)
    return {'SOCIAL': social, 'SHOW_SPONSORS':SHOW_SPONSORS}