# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Team, Profile, TeamNotification

admin.site.register(Profile)
admin.site.register(Team)
admin.site.register(TeamNotification)