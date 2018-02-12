"""Declare models for portal app."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


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

class PlayerManager(models.Manager):
    use_for_related_fields = True

    def add_player(self, user, team):
        pass

    def remove_player(self, user, team):
        pass

class Player(models.Model):
    user = models.ForeignKey(MyUser)
    team = models.ForeignKey(Team)
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
    
