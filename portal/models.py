# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tournament(models.Model):
    tournament_name = models.CharField(max_length=200,default=None)
    tournament_date = models.DateTimeField(default=None,null=True)
    no_of_players = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.tournament_name

class Team(models.Model):
    team_head = models.ForeignKey(User,default=None, null=True)
    team_name = models.CharField(max_length=200)
    team_info = models.TextField(default=None, null=True)
    team_link = models.CharField(max_length=255, default=None, null=True)
    tournament = models.CharField(max_length=200, default=None, null=True)
    number_of_players = models.IntegerField(default=0)
    game_on = models.IntegerField(default=0)
    team_lock = models.IntegerField(default=0)
    team_avatar = models.ImageField(upload_to="team_image", blank=True)
    
    def __str__(self):
        return self.team_name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    steam_id = models.CharField(max_length=200,default=None,null=True)
    location = models.CharField(max_length=200,default='India',null=True)
    avatar = models.ImageField(upload_to="profile_image", blank=True)
    status_CS = models.IntegerField(default=0, null=True)
    status_FIFA = models.IntegerField(default=0, null=True)
    team_cs = models.ForeignKey(Team,default=None,null=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class TeamNotification(models.Model):
    team = models.ForeignKey(Team,default=None,null=True)
    user = models.ForeignKey(User,default=None,null=True)

    def __str__(self):
        return self.team
    
