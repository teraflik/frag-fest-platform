import os
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager

def avatar_upload(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("avatars", filename)

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
    name = models.CharField(max_length=100, verbose_name=_("name"))
    avatar = models.ImageField(upload_to=avatar_upload, blank=True, verbose_name=_("avatar"))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="teams_created", verbose_name=_("creator"), on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now, editable=False, verbose_name=_("created"))
    info = models.TextField(blank=True, verbose_name=_("description"))
    link = models.CharField(max_length=255, blank=True, verbose_name=_("social_link"))
    locked = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    def lock(self):
        if self.locked:
            raise ValueError('Team is already locked!')
        self.locked = 1

    def can_leave(self, user):
        # owners can't leave at the moment
        role = self.role_for(user)
        return role == BaseMembership.ROLE_MEMBER

    def can_apply(self, user):
        state = self.state_for(user)
        return not self.locked and state is None and user.profile.valid()
    
    @property
    def applicants(self):
        return self.memberships.filter(state=BaseMembership.STATE_APPLIED)
    
    @property
    def rejections(self):
        return self.memberships.filter(state=BaseMembership.STATE_REJECTED)
    
    @property
    def acceptances(self):
        return self.memberships.filter(state=BaseMembership.STATE_ACCEPTED)
    
    @property
    def members(self):
        return self.acceptances.filter(role=BaseMembership.ROLE_MEMBER)
    
    @property
    def owners(self):
        return self.acceptances.filter(role=BaseMembership.ROLE_OWNER)

    def is_member(self, user):
        return self.members.filter(user=user).exists()

    def is_owner(self, user):
        return self.owners.filter(user=user).exists()

    def is_on_team(self, user):
        return self.acceptances.filter(user=user).exists()

    def for_user(self, user):
        try:
            return self.memberships.get(user=user)
        except ObjectDoesNotExist:
            pass

    def state_for(self, user):
        membership = self.for_user(user=user)
        if membership:
            return membership.state

    def role_for(self, user):
        membership = self.for_user(user)
        if membership:
            return membership.role

    def size(self):
        return self.acceptances.count()

class Membership(models.Model):
    STATE_APPLIED = "applied"
    STATE_REJECTED = "rejected" #When team rejects an application
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
        (ROLE_OWNER, _("owner"))
    ]

    state = models.CharField(max_length=20, choices=STATE_CHOICES, verbose_name=_("state"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER, verbose_name=_("role"))
    created = models.DateTimeField(default=timezone.now, verbose_name=_("created"))

    user = models.ForeignKey(MyUser, related_name='memberships', null=True, blank=True, verbose_name=_("user"), on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, related_name='memberships', verbose_name=_("team"), on_delete=models.CASCADE)

    def __str__(self):
        return "{0} in {1}".format(self.user, self.team)
    
    class Meta:
        unique_together=[("team", "user")]
        verbose_name=_("Membership")
        verbose_name_plural=_("Memberships")
    
    def is_owner(self):
        return self.role == BaseMembership.ROLE_OWNER

    def is_member(self):
        return self.role == BaseMembership.ROLE_MEMBER

    def accept(self, by):
        role = self.team.role_for(by)
        if role in [Membership.ROLE_OWNER]:
            if self.state == Membership.STATE_APPLIED:
                self.state = Membership.STATE_ACCEPTED
                self.save()
                signals.accepted_membership.send(sender=self, membership=self)
                return True
        return False

    def reject(self, by):
        role = self.team.role_for(by)
        if role in [Membership.ROLE_OWNER]:
            if self.state == Membership.STATE_APPLIED:
                self.state = Membership.STATE_REJECTED
                self.save()
                signals.rejected_membership.send(sender=self, membership=self)
                return True
        return False

    def status(self):
        if self.user:
            return self.get_state_display()
        return "Unknown"

    def remove(self, by=None):
        self.delete()
        signals.removed_membership.send(
            sender=Membership, team=self.team, user=self.user, invitee=self.invitee, by=by)

class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    steam_connected = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255, blank=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    def valid(self):
        return self.steam_connected and self.email_confirmed

@receiver(post_save, sender=MyUser)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
