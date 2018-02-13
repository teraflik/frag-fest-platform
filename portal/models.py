"""Declare models for portal app."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import UserManager

class MyUser(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(
        _('email address'), 
        max_length=255,
        unique=True, 
        error_messages={
            'unique': _("A user with that email already exists."),
        },)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class Team(models.Model):
    captain = models.ForeignKey(
        MyUser, related_name="teams_created", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False)
    info = models.TextField(default=None, blank=True)
    link = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to="portal/team_logo", null=True, blank=True)
    game_on = models.IntegerField(default=0)
    locked = models.BooleanField(default=False)
    players = models.ManyToManyField(MyUser, through='Player')

    def __str__(self):
        return self.team_name

    def lock(self):
        if self.locked:
            raise ValueError('Team is already locked!')
        self.locked = 1
    
    def no_of_players(self):
        return self.players.count()

class PlayerManager(models.Manager):
    use_for_related_fields = True

    def add_player(self, user, team):
        pass

    def remove_player(self, user, team):
        pass

class Player(models.Model):
    STATE_APPLIED = "applied"
    STATE_REJECTED = "rejected"
    STATE_ACCEPTED = "accepted"

    ROLE_MEMBER = "member"
    ROLE_OWNER = "owner"

    STATE_CHOICES = [
        (STATE_APPLIED, _("applied")),
        (STATE_REJECTED, _("rejected")),
        (STATE_ACCEPTED, _("accepted")),
    ]
    
    ROLE_CHOICES = [
        (ROLE_MEMBER, _("member")),
        (ROLE_MANAGER, _("manager")),
        (ROLE_OWNER, _("owner"))
    ]

    user = models.ForeignKey(MyUser, related_name='membership')
    team = models.ForeignKey(Team, related_name='membership')
    role = models.ChoiceField()
    objects = PlayerManager()

class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True)
    steam_id = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, default='India', blank=True)
    avatar = models.ImageField(upload_to="profile_image", null=True, blank=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    @property
    def get_steam_id(self):
        if self.steam_id is not None and self.steam_id != "":
            return self.steam_id
        return None

@receiver(post_save, sender=MyUser)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class TeamNotification(models.Model):
    team = models.ForeignKey(Team,default=None,null=True)
    user = models.ForeignKey(MyUser,default=None,null=True)

    def __str__(self):
        return self.team
    
