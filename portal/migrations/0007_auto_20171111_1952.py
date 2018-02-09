# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-11 19:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0006_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='teamHead',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
