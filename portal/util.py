from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from collections import OrderedDict

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.profile.email_confirmed)
        )

account_activation_token = AccountActivationTokenGenerator()

def social_links(request):
    social = [
        ('facebook', 'https://www.facebook.com/FragFestIIITA/'),
        ('twitter', 'https://twitter.com/FragFestIIITA/'),
        ('youtube-play', 'https://www.youtube.com/channel/UCsuoNyw1L8W58mXAsXZ90ZA'),
        ('google-plus', 'https://plus.google.com/+FragFest'),
        ('twitch', 'https://www.twitch.tv/FragFestIIITA/'),
        ('steam', 'https://steamcommunity.com/groups/Frag-Fest')
    ]
    social = OrderedDict(social)
    return {'SOCIAL': social}