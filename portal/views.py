# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render,redirect,render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from .models import Player,Team,Tournament,Profile,TeamNotification
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm,TournamentForm,TeamForm,UpdateForm,ProfileForm,PlayerForm,DeleteTeamForm, changepass, forgetpass, subscriptionform
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.db.models import Q
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import requests
import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):  # randon id generator for e-mail password funtionality
    return ''.join(random.choice(chars) for _ in range(size))

class IndexView(generic.ListView):
    template_name = 'portal/index.html'

    def get_queryset(self):
        return Player.objects.filter().order_by('player')

class Register(View):
    template_name = 'portal/register.html'
    form_class = UserForm
    form_class2 = forgetpass
    form_class3 = subscriptionform
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portal:home')
            
        else:
            form = self.form_class(None)
            form2 = self.form_class2(None)
            form3 = self.form_class3(None)
            return render(request, self.template_name, {'form': form, 'form2':form2,'form3':form3})
        
    #process form data
    def post(self, request):
        form = self.form_class(request.POST)
        form2 = self.form_class2(request.POST)
        form3 = self.form_class3(request.POST)
        
        if form.is_valid():
            user1 = User.objects.create_user(username=form.cleaned_data['username'],email=form.cleaned_data['email'],first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'])
            #cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user1.set_password(password)
            user1.save()
            profile = Profile.objects.create(user=user1,steam_id=None,location=None)
            profile.id = user1.id
            profile.save()

            if form3.is_valid():
                profile.is_subscription=form3.cleaned_data['is_subscribe']
                profile.save()

            user2 = authenticate(username = username, password= password)
            if user2 is not None:
                login(request, user2)
                subject = 'Thankyou for registering'
                message = 'Welcome to fragfest 2018.'
                from_email = settings.EMAIL_HOST_USER
                to_list = [user2.email,settings.EMAIL_HOST_USER]
                send_mail(subject,message,from_email,to_list,fail_silently=True)
                return redirect('portal:index')
            else:
                return render(request, self.template_name, {'form': form, 'form2':form2,'form3':form3})

        if form2.is_valid():
            username123 = form2.cleaned_data['usernamee']

            usercount = User.objects.filter(username=form2.cleaned_data['usernamee']).count()
            if usercount==1:
                user = User.objects.get(username=username123)
                password = id_generator()
                user.set_password(password)
                user.save()

                #send_mail(subject, message, from_email, to_list, fail_silently=True)
                subject = 'Password change'
                message = 'You forgot your passwordso we are sending new password. Change this password once you log in. Your username = ' + username123 + ' Your new password = ' + password
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject,message,from_email,to_list,fail_silently=True)

                messages.success(request, 'Your password was successfully sent!')
                return redirect('portal:login')
            else:
                return render(request, self.template_name, {'form': form, 'form2':form2,'form3':form3})

        return render(request, self.template_name, {'form': form, 'form2':form2,'form3':form3})
        
class TeamView(View):
    template_name = 'portal/teams.html'
    def get(self, request):
        cs = Team.objects.filter(tournament="CS")
        return render(request, self.template_name, {'cs': cs})

    
@login_required
def ProfileView(request):
    template_name = 'portal/profile.html'

    if request.method == "POST":
        detail = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(id=request.user.id)
        user_form = UpdateForm(request.POST)
        profile_form = ProfileForm(request.POST)
        changepassword_form = PasswordChangeForm(request.user, request.POST)
            
        if changepassword_form.is_valid():
            user = changepassword_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('portal:profile')

        else:
            if user_form.is_valid() and user_form.cleaned_data['username']!='' :
                uniqueUser = User.objects.filter(username=user_form.cleaned_data['username'])
                if uniqueUser.count() > 0:
                    uniqueUser2 = User.objects.get(username=user_form.cleaned_data['username'])
                    if uniqueUser2.id != request.user.id:
                        return render(request, template_name,{'detail':detail,'profile':profile,'user_form':user_form,'profile_form':profile_form, 'changepassword_form':changepassword_form})
            
                detail.username = user_form.cleaned_data['username']
                detail.save()

            if profile_form.is_valid():
                if profile_form.cleaned_data['steam_id']!=None and profile_form.cleaned_data['steam_id']!='':
                    profile.steam_id = profile_form.cleaned_data['steam_id']

                if profile_form.cleaned_data['location']!=None:
                    profile.location = profile_form.cleaned_data['location']
                profile.save()
            else:
                messages.failure(request, 'Error!')
    else:
        detail = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(id=request.user.id)
        user_form = UpdateForm(None)
        profile_form = ProfileForm(None)
        changepassword_form = PasswordChangeForm(request.user)
    return render(request, template_name,{'detail':detail,'profile':profile,'user_form':user_form,'profile_form':profile_form, 'changepassword_form':changepassword_form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('portal:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'portal/change_password.html', {
        'form': form
    })

class dashboard(View):
    template_name = 'portal/dashboard.html'
    form_class = TeamForm
    form_class2 = PlayerForm
    def get(self,request):

        profiles = None
        team_form = self.form_class(None)
        member_form = self.form_class2(None)
        count=0
        notifications = None
        team1=None

        players = None
        if request.user.is_authenticated():
            profiles = Profile.objects.get(id=request.user.id)
            if profiles.status_CS==1:
                team1 = profiles.team_cs
                notifications = TeamNotification.objects.filter(team=team1)
                players = Profile.objects.filter(team_cs=team1)
                count=players.count();
                if notifications.count()==0:
                    notifications=None

        return render(request, self.template_name,{'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})
    def post(self,request):
        team_form = self.form_class(request.POST)
        member_form = self.form_class2(request.POST)
        profiles = None
        count=0

        if team_form.is_valid():
            uniqueTeam = Team.objects.filter(team_name=team_form.cleaned_data['team_name'],tournament='CS')
            if uniqueTeam.count() > 0:
                uniqueTeam = Team.objects.get(team_name=team_form.cleaned_data['team_name'],tournament='CS')
                if TeamNotification.objects.filter(team=uniqueTeam,user=request.user).count()==0:
                    notification = TeamNotification.objects.create(team=uniqueTeam,user=request.user)
                    notification.save()
                return redirect('portal:profile', user_id=request.user.id)
            else:
                newTeam = Team.objects.create(team_head=request.user,team_name=team_form.cleaned_data['team_name'],tournament='CS')
                uniqueUser = Profile.objects.get(id=request.user.id)
                uniqueUser.status_CS = 1
                newTeam.save()
                uniqueUser.team_cs = newTeam
                uniqueUser.save()
                notifications = None
                team1=None
                count=0
                players = None
                if request.user.is_authenticated():
                    profiles = Profile.objects.get(id=request.user.id)
                    if profiles.status_CS==1:
                        team1 = profiles.team_cs
                        notifications = TeamNotification.objects.filter(team=team1)
                        players = Profile.objects.filter(team_cs=team1)
                        count=players.count();
                        if notifications.count()==0:
                            notifications=None
                return render(request, self.template_name,{'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})


        if member_form.is_valid():
            uniqueUser = User.objects.filter(username=member_form.cleaned_data['player'])
            if uniqueUser.count()!=0:
                user1 = User.objects.get(username=member_form.cleaned_data['player'])
                uniqueUser = Profile.objects.get(user=user1)
                team1 = profiles.team_cs
                if uniqueUser.status_CS==0:
                    uniqueUser.status_CS = 1
                    uniqueUser.team_cs = team1
                    uniqueUser.save()
        
        profiles = None
        notifications = None
        count=0
        team1=None
        players = None
        if request.user.is_authenticated():
            profiles = Profile.objects.get(id=request.user.id)
            if profiles.status_CS==1:
                team1 = profiles.team_cs
                notifications = TeamNotification.objects.filter(team=team1)
                players = Profile.objects.filter(team_cs=team1)
                count=players.count();
                if notifications.count()==0:
                    notifications=None

        return render(request, self.template_name,{'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})


def CSTeamConfirmView(request,team_id,user_id):
    team_id1 = team_id
    team1 = Team.objects.get(id=team_id)
    if request.method == "GET" and request.user==team1.team_head and Profile.objects.get(id=user_id).status_CS==0 and Profile.objects.filter(team_cs=team1).count()<5:
        uniqueTeam = Team.objects.get(id=team_id)
        user1 = User.objects.get(id=user_id)
        profiles = Profile.objects.get(id=user_id)
        profiles.status_CS=1
        profiles.team_cs=uniqueTeam
        profiles.save()
        notification = TeamNotification.objects.get(team=uniqueTeam,user=user1)
        notification.delete()
        return redirect('portal:dashboard',team_id = team_id1)


def DeleteTeam(request, team_id):
    team1 = Team.objects.get(id=team_id)
    if request.user==team1.team_head:
        players = Profile.objects.filter(team_cs=team1)
        for player in players:
            player.status_CS=0
            player.team_cs=None
            player.save()
        team1.delete()
        return redirect('portal:index')
    else:
        return redirect('portal:dashboard')


def RemovePlayer(request,team_id,user_id):
    team_id1=team_id
    team1=Team.objects.get(id=team_id)
    if request.user==team1.team_head:
        profiles = Profile.objects.get(id=user_id)
        profiles.status_CS=0
        profiles.team_cs=None
        return redirect('portal:dashboard')

    return redirect('portal:index')    
    
    

def logout_view(request):
    logout(request)
    return redirect('portal:index')

def home(request):
    template_name = 'portal/index.html'
    return render(request, template_name)