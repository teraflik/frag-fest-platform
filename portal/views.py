from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from portal.forms import SignUpForm, UserForm, TeamForm, ProfileForm, PlayerForm, DeleteTeamForm, forgetpass
from portal.tokens import account_activation_token
from django.contrib import messages
from django.core.mail import send_mail
from portal.models import Team, Tournament, Profile, TeamNotification
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.generic import View

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
import requests
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):  # randon id generator for e-mail password funtionality
    return ''.join(random.choice(chars) for _ in range(size))

def index(request):
    template_name = 'portal/index.html'
    return render(request, template_name)

@login_required
def send_verification_email(request):
    user = request.user
    current_site = get_current_site(request)
    subject = 'Your ' + current_site.name + ' account has been created. Please verify your email.'
    message = render_to_string('portal/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.is_subscribed = form.cleaned_data.get('subscribe')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            current_site = get_current_site(request)
            subject = 'Your ' + current_site.name + ' account has been created. Please verify your email.'
            message = render_to_string('portal/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.success(request, _('Successfully registered! We have sent you a verification email.'))
            return redirect('portal:home')
    else:
        form = SignUpForm()
    return render(request, 'portal/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        messages.success(request, _('Email verified successfully.'))
        return redirect('portal:index')
    elif user is not None and user.profile.email_confirmed == True:
        messages.success(request, _('Email already verified!'))
    else:
        messages.error(request, _('Email verification error!'))
    return render(request, 'portal/index.html')

'''
login(request, user2)
subject = 'Thank you for registering'
message = 'Welcome to fragfest 2018.'
from_email = settings.EMAIL_HOST_USER
to_list = [user2.email,settings.EMAIL_HOST_USER]
send_mail(subject,message,from_email,to_list,fail_silently=True)
return redirect('portal:index')

password = id_generator()
user.set_password(password)
user.save()
subject = 'Password change'
message = 'You forgot your passwordso we are sending new password. Change this password once you log in. Your username = ' + username123 + ' Your new password = ' + password
from_email = settings.EMAIL_HOST_USER
to_list = [user.email]
send_mail(subject,message,from_email,to_list,fail_silently=True)

messages.success(request, 'Your password was successfully sent!')'''

@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        if 'updateProfile' in request.POST:
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, _('Your profile was successfully updated!'))
                return redirect('portal:profile')
            else:
                messages.error(request, _('Could not update Profile.'))
                password_form = PasswordChangeForm(request.user)
        elif 'changePassword' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Your password was successfully updated!'))
                return redirect('portal:profile')
            else:
                messages.error(request, _('Could not change password. '))
                user_form = UserForm(instance=request.user)
                profile_form = ProfileForm(instance=request.user.profile)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'portal/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form
    })


class TeamView(View):
    template_name = 'portal/teams.html'

    def get(self, request):
        cs = Team.objects.filter(tournament="CS")
        return render(request, self.template_name, {'cs': cs})


def SingleTeam(request, team_id):
    template_name = 'portal/single_team.html'
    if Team.objects.filter(id=team_id).count() != 0:
        team = Team.objects.get(id=team_id)
        players = Profile.objects.filter(team_cs=team)
        return render(request, template_name, {'team': team, 'players': players})
    else:
        return redirect('portal:index')

class dashboard(View):
    template_name = 'portal/dashboard.html'
    def get(self,request):
        profiles = None
        team_form = TeamForm(None)
        member_form = PlayerForm(None)
        count=0
        notifications = None
        team1=None
        captain=None
        players = None
        if request.user.is_authenticated():
            profiles = Profile.objects.get(id=request.user.id)
            if profiles.status_CS==1:
                team1 = profiles.team_cs
                captain=team1.team_head.username
                notifications = TeamNotification.objects.filter(team=team1)
                players = Profile.objects.filter(team_cs=team1)
                count=players.count();
                if notifications.count()==0:
                    notifications=None

        return render(request, self.template_name,{'captain':captain,'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})
    def post(self,request):
        team_form = TeamForm(request.POST)
        member_form = PlayerForm(request.POST)
        profiles = None
        count=0
        captain=None
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
                        captain=team1.team_head.username
                        notifications = TeamNotification.objects.filter(team=team1)
                        players = Profile.objects.filter(team_cs=team1)
                        count=players.count();
                        if notifications.count()==0:
                            notifications=None
                return render(request, self.template_name,{'captain':captain,'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})


        if member_form.is_valid():
            uniqueUser = User.objects.filter(username=member_form.cleaned_data['player'])
            if uniqueUser.count()!=0:
                profiles = Profile.objects.get(id=request.user.id)
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
                captain=team1.team_head.username
                notifications = TeamNotification.objects.filter(team=team1)
                players = Profile.objects.filter(team_cs=team1)
                count=players.count();
                if notifications.count()==0:
                    notifications=None

        return render(request, self.template_name,{'captain':captain,'profiles':profiles,'players':players,'count':count,'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form})


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
