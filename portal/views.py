import requests
import json
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.template.loader import render_to_string
from portal.util import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.views.generic import View, FormView, ListView

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from social_core.backends.steam import SteamOpenId
from social_core.backends.open_id import OpenIdAuth

from .models import MyUser, Team, Profile, Membership
from .forms import SignUpForm, ProfileForm, TeamForm, TeamUpdateForm

def index(request):
    template_name = 'stat/index.html'
    return render(request, template_name)

@login_required
def send_verification_email(request):
    user = request.user
    current_site = get_current_site(request)
    subject = 'Your ' + current_site.name + ' account has been created. Please verify your email.'
    html_message = render_to_string('email/email_activation_html.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    plain_message = render_to_string('email/email_activation_plain.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()

def signup(request):
    if request.user.is_authenticated:
        messages.info(request, _('You are already registered!'))
        return redirect('portal:index')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.is_subscribed = form.cleaned_data.get('subscribe')
            user.profile.display_name = form.cleaned_data.get('first_name') + " " +form.cleaned_data.get('last_name')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            login(request, user)
            send_verification_email(request)
            messages.success(request, _('Successfully registered! We have sent you a verification email. Check your spam as well.'))
            return redirect('portal:index')
    else:
        form = SignUpForm()
    return render(request, 'portal/signup.html', {'form': form})

@login_required
def resend_verification(request):
    if request.user.profile.email_confirmed:
        messages.info(request, _('Email already verified!'))
        return redirect('portal:profile')
    else:
        send_verification_email(request)
        messages.info(request, _('Verification email resent. If you can\'t find it, check your spam folder.'))
        return redirect('portal:profile')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.profile.email_confirmed = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, _('Email verified successfully.'))
        return redirect('portal:index')
    elif user is not None and user.profile.email_confirmed == True:
        messages.success(request, _('Email already verified!'))
    else:
        messages.error(request, _('Email verification error!'))
    return render(request, 'stat/index.html')

@login_required
@transaction.atomic
def profile(request):
    if request.user.profile.steam_connected:
        steam_id = request.user.social_auth.get(provider='steam').uid
        steam = request.user.social_auth.get(provider='steam').extra_data['player'] #All player details.
    else:
        steam_id = None
        steam = None

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
        'steam_id': steam_id,
        'steam': steam,
    })

def steam_connect(request):
    if request.user.is_authenticated():
        user = request.user
        #user.refresh_from_db()  # load the profile instance created by the signal
        user.profile.steam_connected = True
        user.save()
        messages.success(request, _('Steam authentication successful!'))
        return redirect('portal:profile')
    else:
        raise Http404("Invalid Request!")

class TeamListView(ListView):
    model = Team
    context_object_name = "teams"
    template_name = "portal/team_list.html"

################################### TEAM HANDLING BELOW THIS #################################

def team_view(request, pk, dashboard=False):
    team = get_object_or_404(Team, pk=pk)
    
    if not request.user.is_authenticated():
        return render(request, 'portal/team.html', {'team': team, 'can_apply': False})
    
    if request.user.profile.only_team() is None:
        return render(request, 'portal/team.html', {'team': team, 'can_apply': True})

    if request.user.profile.only_team().pk != team.pk:
        return render(request, 'portal/team.html', {'team': team, 'can_apply': False})

    state = team.state_for(request.user)
    role = team.role_for(request.user)

    if request.method == 'POST':
        team_form = TeamUpdateForm(request.POST, instance=team)
        if team_form.is_valid():
            team = team_form.save()
            messages.add_message(request, messages.SUCCESS, _('Team details were successfully updated!'))
            return redirect('portal:dashboard')
        else:
            messages.error(request, _('There were some errors updating the team.'))
    else:
        team_form = TeamUpdateForm()

    captain_steam_id = team.creator.social_auth.get(provider='steam').uid
    '''steam_ids = []
    for member in team.acceptances:
        steam_ids.append(member.user.social_auth.get(provider='steam').uid)'''

    return render(request, 'portal/team_manage.html', {
                                                'team': team,
                                                'owner': role == Membership.ROLE_OWNER,
                                                'captain_steam_id': captain_steam_id,
                                                'team_form': team_form,
                                                'applicants': team.applicants
                                                })

def dashboard(request):
    title = 'Team Dashboard'
    if not request.user.is_authenticated():
        message = 'You need to be logged in to access your Team Dashboard.'
        action = 'log_in'
        return render(request, 'portal/no_access.html', {'title': title, 'message': message, 'action': action})

    if not request.user.profile.steam_connected:
        message = 'You need to be signed-in to Steam to join a Team.'
        action = 'connect_steam'
        return render(request, 'portal/no_access.html', {'title': title, 'message': message, 'action': action})

    team = request.user.profile.only_team()
    if team is not None:
        return team_view(request, team.pk, dashboard=True) 
    else:
        teams_available = Team.objects.filter(locked=False)

        if request.method == 'POST':
            create_team_form = TeamForm(request.POST)
            if create_team_form.is_valid():
                team = create_team_form.save(commit=False)
                team.creator = request.user
                team.save() #A post-save signal is used to create the membership for the owner
                messages.success(request, _('Your team was successfully created. You are now its manager.'))
                return redirect('portal:dashboard')
            else:
                messages.error(request, _('There were some errors creating the team.'))
        else:
            create_team_form = TeamForm()

        return render(request, 'portal/dashboard.html', {'team_form': create_team_form, 'teams_available': teams_available})


@login_required
@require_POST
def team_accept(request, pk):
    """Accept a user who has has membership status set as APPLIED."""
    membership = get_object_or_404(Membership, pk=pk)
    team = membership.team
    try:
        player = Membership.objects.get(user=membership.user, state=Membership.STATE_ACCEPTED)
    except Membership.DoesNotExist:
        player = None
    if player is None and membership.accept(by=request.user):
        messages.success(request, _('Accepted player application.'))
    else:
        membership.remove(by=request.user)
        messages.info(request, _('Cannot accept player application. Already part of another team.'))
    return redirect('portal:team', pk=team.pk)
    
@login_required
@require_POST
def team_reject(request, pk):
    """Reject a user who has has membership status set as APPLIED."""
    membership = get_object_or_404(Membership, pk=pk)
    team = membership.team
    if membership.reject(by=request.user):
        messages.info(request, _('Rejected player application. The player will not be able to send any further requests.'))
    return redirect('portal:team', pk=team.pk)

@login_required
@require_POST
def team_apply(request, pk):
    team = get_object_or_404(Team, pk=pk)

    if team.can_apply(request.user):
        membership, created = Membership.objects.get_or_create(team=team, user=request.user)
        membership.state = Membership.STATE_APPLIED
        membership.save()
        messages.success(request,  _('You have successfully applied to the team. Wait for the manager to accept.'))
    else:
        messages.error(request,  _('Error applying for the team. Make sure your profile is complete and you are not already in a team.'))
    return redirect('portal:team', pk=pk)

@login_required
@require_POST
def team_leave(request, pk):
    team = get_object_or_404(Team, pk=pk)
    state = team.state_for(request.user)
    if state is None:
        raise Http404()

    if team.can_leave(request.user):
        membership = Membership.objects.get(team=team, user=request.user)
        membership.delete()
        messages.success(request, _('You have left the team.'))
        return redirect('portal:index')
    else:
        messages.error(request, _('You cannot leave the team.'))
        return redirect('portal:team', pk=pk)

@login_required
@require_POST
def team_lock(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if team.is_owner(request.user):
        try:
            team.lock()
            messages.info(request, _('You have locked the team. User applications have been closed now.'))
        except:
            messages.error(request, _('Error locking the team.'))
    else:
        raise Http404()
    return redirect('portal:team', pk=pk)

@login_required
@require_POST
def team_unlock(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if team.is_owner(request.user):
        try:
            team.unlock()
            messages.info(request, _('You have unlocked the team. User applications will be accepted now.'))
        except:
            messages.error(request, _('Error unlocking the team.'))
    else:
        raise Http404()
    return redirect('portal:team', pk=pk)

