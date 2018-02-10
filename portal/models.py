# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

class Tournament(models.Model):
    tournament_name = models.CharField(max_length=200,default=None)
    tournament_date = models.DateTimeField(default=None,null=True)
    no_of_players = models.IntegerField(default=1, null=True)
    def __unicode__(self):
        return unicode(self.tournament_name)

    def __str__(self):
        return self.tournament_name

class Team(models.Model):
    team_head = models.ForeignKey(User,default=None,null=True)
    team_name = models.CharField(max_length=200, default=None)
    #tournament = models.ForeignKey(Tournament,default=None,null=True)
    tournament = models.CharField(max_length=200, default=None)
    number_of_players = models.IntegerField(default=0, null=True)
    game_on = models.IntegerField(default=0, null=True)
    team_lock = models.IntegerField(default=0, null=True)
    team_avatar = models.ImageField(upload_to="team_image", blank=True)
    
    def __unicode__(self):
        return unicode(self.team_name)

    def __str__(self):
        return self.team_name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steam_id = models.CharField(max_length=200,default=None,null=True)
    location = models.CharField(max_length=200,default=None,null=True)
    user_avatar = models.ImageField(upload_to="profile_image", blank=True)
    status_CS = models.IntegerField(default=0, null=True)
    status_FIFA = models.IntegerField(default=0, null=True)
    status_DOTA = models.IntegerField(default=0, null=True)
    team_cs = models.ForeignKey(Team,default=None,null=True)
    is_subscribe = models.BooleanField(default=True)
    def __unicode__(self):
        return unicode(self.user)

    def __str__(self):
        return self.user

class TeamNotification(models.Model):
    team = models.ForeignKey(Team,default=None,null=True)
    user = models.ForeignKey(User,default=None,null=True)

    def __unicode__(self):
        return unicode(self.team)

    def __str__(self):
        return self.team
    
