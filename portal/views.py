from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.views.generic import View, FormView, ListView
from portal.tokens import account_activation_token
from django.contrib import messages
from django.core.mail import send_mail
from portal.models import MyUser, Team, Profile, Membership, TeamNotification
from django.contrib.auth import authenticate, login, update_session_auth_hash

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext as _

from portal.forms import SignUpForm, TeamForm, ProfileForm, forgetpass
def index(request):
    template_name = 'portal/index.html'
    return render(request, template_name)

@login_required
def send_verification_email(request, user):
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
            user = authenticate(email=user.email, password=raw_password)
            login(request, user)
            send_verification_email(request, user)
            messages.success(request, _('Successfully registered! We have sent you a verification email.'))
            return redirect('portal:index')
    else:
        form = SignUpForm()
    return render(request, 'portal/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
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
subject = 'Password change'
message = 'You forgot your password so we are sending new password. Change this password once you log in. Your username = ' + username123 + ' Your new password = ' + password
from_email = settings.EMAIL_HOST_USER
to_list = [user.email]
send_mail(subject,message,from_email,to_list,fail_silently=True)

messages.success(request, 'Your password was successfully sent!')'''

@login_required
@transaction.atomic
def profile(request):
    email_confirmed = request.user.profile.email_confirmed
    if request.method == 'POST':
        if 'updateProfile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.add_message(request, messages.SUCCESS, _('Your profile was successfully updated!'))
                return redirect('portal:profile')
            else:
                messages.add_message(request, messages.ERROR, _('Could not update Profile.'))
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
                profile_form = ProfileForm(instance=request.user.profile)
    else:
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'portal/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'email_confirmed': email_confirmed
    })

class TeamListView(ListView):
    model = Team
    context_object_name = "teams"
    template_name = "portal/team_list.html"

@login_required
def manage_team(request):
    teams = Team.objects.filter(memberships=request.user.memberships.all())

    return render(request, 'portal/dashboard.html', {'teams': teams})

@login_required
def create_or_join(request):
    if request.method == 'POST':
        create_team_form = TeamForm(request.POST)
        if create_team_form.is_valid():
            team = create_team_form.save(commit=False)
            team.creator = request.user
            team.save()
            membership = Membership.objects.create(team=team, user=request.user, role=Membership.ROLE_OWNER, state=Membership.STATE_ACCEPTED)
            membership.save()
            messages.success(request, _('Your team was succesfully created!'))
            return redirect('portal:team_list')
    else:
        create_team_form = TeamForm()
    return render(request, 'portal/create_or_join.html', {'create_form': create_team_form})

def dashboard(request):
    if not request.user.is_authenticated():
        message = 'You need to be logged in to access your Team Dashboard.'
        return render(request, 'portal/no_access.html', {'title': 'Team Dashboard', 'message': message})
    
    if request.user.profile.get_steam_id is None:
        message = 'You need to be signed into Steam to join a Team.'
        return render(request, 'portal/no_access.html', {'title': 'Steam Error', 'message': message})

    memberships = request.user.memberships.all()

    if memberships.exists():
        result = manage_team(request)
    else:
        result = create_or_join(request)
    return result

def SingleTeam(request, team_id):
    template_name = 'portal/single_team.html'
    if Team.objects.filter(id=team_id).count() != 0:
        team = Team.objects.get(id=team_id)
        players = Profile.objects.filter(team_cs=team)
        return render(request, template_name, {'team': team, 'players': players})
    else:
        return redirect('portal:index')

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


def fifa(request):
    template_name = 'portal/fifa.html'
    return render(request, template_name)


def csgo(request):
    template_name = 'portal/csgo.html'
    return render(request, template_name)
