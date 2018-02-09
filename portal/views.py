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
from .forms import UserForm,TournamentForm,TeamForm,UpdateForm,ProfileForm,PlayerForm,DeleteTeamForm, changepass, forgetpass
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
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portal:home')
            
        else:
            form = self.form_class(None)
            form2 = self.form_class2(None)
            
            return render(request, self.template_name, {'form': form, 'form2':form2})
        
    #process form data
    def post(self, request):
        form = self.form_class(request.POST)
        form2 = self.form_class2(request.POST)
        
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
            user2 = authenticate(username = username, password= password)
            if user2 is not None:
                login(request, user2)
                subject = 'Thankyou for registering'
                message = 'Welcome to fragfest 2018.'
                from_email = settings.EMAIL_HOST_USER
                to_list = [user2.email,settings.EMAIL_HOST_USER]
                send_mail(subject,message,from_email,to_list,fail_silently=True)
                return redirect('portal:home')
            else:
                return render(request, self.template_name, {'form': form, 'form2':form2})

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
                return render(request, self.template_name, {'form': form, 'form2':form2})

        return render(request, self.template_name, {'form': form, 'form2':form2})
        
class TeamView(View):
    template_name = 'portal/teams.html'
    def get(self, request):
        cs = Team.objects.filter(tournament="CS")
        dota = Team.objects.filter(tournament="DOTA")
        return render(request, self.template_name, {'cs': cs, 'dota':dota})

    

def user_detail(request,user_id):
    template_name = 'portal/details.html'
    form_class = UpdateForm
    form_class1 = ProfileForm
    form_class2 = changepass
    if request.method == "GET":
        #print(user_id)
        detail = User.objects.get(id=user_id)
        profile = Profile.objects.get(id=user_id)
        csteam = None
        dotateam = None
        if profile.status_CS==1:
            csteam = profile.team_cs
               
                
        form = form_class(None)
        form1 = form_class1(None)
        form2 = form_class2(None)
        return render(request, template_name,{'detail':detail,'profile':profile,'form':form,'form1':form1, 'form2':form2,'csteam':csteam,'dotateam':dotateam})

    if request.method == "POST":
        
        detail = User.objects.get(id=user_id)
        profile = Profile.objects.get(id=user_id)
        form = form_class(request.POST)
        form1 = form_class1(request.POST)
        form2 = form_class2(request.POST)
        csteam = None
        if profile.status_CS==1:
            csteam = profile.team_cs
            
        if form.is_valid():
            print(11111111111111)
            uniqueUser = User.objects.filter(username=form.cleaned_data['username'])
            if uniqueUser.count() > 0:
                uniqueUser2 = User.objects.get(username=form.cleaned_data['username'])
                if uniqueUser2.id != request.user.id:
                    return render(request, template_name,{'detail':detail,'profile':profile,'form':form,'form1':form1, 'form2':form2, 'csteam':csteam,'dotateam':dotateam})

            player = Profile.objects.get(user = detail)
            if player.status_CS == 1:
                if Team.objects.filter(player1=detail.username).count()!=0:
                    team1=Team.objects.get(player1=detail.username)
                    team1.player1 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player2=detail.username).count()!=0:
                    team1=Team.objects.get(player2=detail.username)
                    team1.player2 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player3=detail.username).count()!=0:
                    team1=Team.objects.get(player3=detail.username)
                    team1.player3 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player4=detail.username).count()!=0:
                    team1=Team.objects.get(player4=detail.username)
                    team1.player4 = form.cleaned_data['username']
                    team1.save()

            if player.status_DOTA == 1:
                if Team.objects.filter(player1=detail.username).count()!=0:
                    team1=Team.objects.get(player1=detail.username)
                    team1.player1 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player2=detail.username).count()!=0:
                    team1=Team.objects.get(player2=detail.username)
                    team1.player2 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player3=detail.username).count()!=0:
                    team1=Team.objects.get(player3=detail.username)
                    team1.player3 = form.cleaned_data['username']
                    team1.save()
                elif Team.objects.filter(player4=detail.username).count()!=0:
                    team1=Team.objects.get(player4=detail.username)
                    team1.player4 = form.cleaned_data['username']
                    team1.save()
                        
            detail.username = form.cleaned_data['username']
            detail.first_name = form.cleaned_data['first_name']
            detail.last_name = form.cleaned_data['last_name']
            detail.email = form.cleaned_data['email']
            detail.save()
            subject = 'Updated email for fragfest'
            message = 'You just updated your profile and email in fragfest 2018 website. Your username = ' + detail.username
            from_email = settings.EMAIL_HOST_USER
            to_list = [detail.email]
            send_mail(subject,message,from_email,to_list,fail_silently=True)
            messages.success(request, 'Your password was successfully sent!')

            if form1.is_valid():
                if form1.cleaned_data['steam_id']!=None and form1.cleaned_data['steam_id']!='':
                    profile.steam_id = form1.cleaned_data['steam_id']
                else:
                    profile.steam_id = None
                if form1.cleaned_data['location']!=None:
                    profile.location = form1.cleaned_data['location']

                profile.save()
                
            if form1.cleaned_data['steam_id']=='':
                profile.steam_id = None
                profile.save()
                            
        print(11111111111)        
        if form2.is_valid():
            print(11111111111111111111111111)
            user = User.objects.get(username=request.user.username)
            user.set_password(form2.cleaned_data['new_pass'])
            user.save()
            
            messages.success(request, 'Your password was successfully updated!')
        
        return render(request, template_name,{'detail':detail,'profile':profile,'form':form,'form1':form1, 'form2':form2, 'csteam':csteam,'dotateam':dotateam})



class dashboard(View):
    template_name = 'portal/dashboard.html'
    form_class = TeamForm
    form_class2 = PlayerForm
    def get(self,request):
        players = User.objects.all()
        profiles = Profile.objects.get(id=request.user.id)
        team_form = self.form_class(None)
        member_form = self.form_class2(None)
        team_head=None
        player1=None
        player2=None
        player3=None
        player4=None
        team_head_user = None
        user1 = None
        user2 = None
        user3 = None
        user4 = None
        notifications = None
        if request.user.is_authenticated():
            if profiles.status_CS==1:

                team1 = profiles.team_cs
                notifications = TeamNotification.objects.filter(team=team1)
                
                team_head = Profile.objects.get(user=team1.team_head)
                team_head_user=User.objects.get(id=team1.team_head.id)
                if team1.player1!=None:
                    user1 = User.objects.get(username=team1.player1)
                    player1 = Profile.objects.get(user=user1)
                    
                if team1.player2!=None:
                    user2 = User.objects.get(username=team1.player2)
                    player2 = Profile.objects.get(user=user2)
                if team1.player3!=None:
                    user3 = User.objects.get(username=team1.player3)
                    player3 = Profile.objects.get(user=user3)
                if team1.player4!=None:
                    user4 = User.objects.get(username=team1.player4)
                    player4 = Profile.objects.get(user=user4)
                
                '''form2=form_class(None)
                form3=form_class2(None)'''
                if notifications.count()==0:
                    notifications=None

        return render(request, self.template_name,{'notifications':notifications,'team1':team1,'team_form':team_form,'member_form':member_form,'team_head':team_head,'team_head_user':team_head_user,'player1':player1,'user1':user1,'player2':player2,'user2':user2,'player3':player3,'user3':user3,'player4':player4,'user4':user4})
    def post(self,request):
        team_form = self.form_class(request.POST)
        member_form = self.form_class2(request.POST)
        players = User.objects.all()
        profiles = Profile.objects.get(id=request.user.id)
        team_head=None
        player1=None
        player2=None
        player3=None
        player4=None
        team_head_user = None
        user1 = None
        user2 = None
        user3 = None
        user4 = None
        notifications = None
        if request.user.is_authenticated():
            if profiles.status_CS==1:

                team1 = profiles.team_cs
                notifications = TeamNotification.objects.filter(team=team1)
                
                team_head = Profile.objects.get(user=team1.team_head)
                team_head_user=User.objects.get(id=team1.team_head.id)
                if team1.player1!=None:
                    user1 = User.objects.get(username=team1.player1)
                    player1 = Profile.objects.get(user=user1)
                    
                if team1.player2!=None:
                    user2 = User.objects.get(username=team1.player2)
                    player2 = Profile.objects.get(user=user2)
                if team1.player3!=None:
                    user3 = User.objects.get(username=team1.player3)
                    player3 = Profile.objects.get(user=user3)
                if team1.player4!=None:
                    user4 = User.objects.get(username=team1.player4)
                    player4 = Profile.objects.get(user=user4)
                
                '''form2=form_class(None)
                form3=form_class2(None)'''
                if notifications.count()==0:
                    notifications=None

        if form.is_valid():
            uniqueTeam = Team.objects.filter(team_name=form.cleaned_data['team_name'],tournament='CS')
            if uniqueTeam.count() > 0:
                uniqueTeam = Team.objects.get(team_name=form.cleaned_data['team_name'],tournament='CS')
                if TeamNotification.objects.filter(team=uniqueTeam,user=request.user).count()==0:
                    notification = TeamNotification.objects.create(team=uniqueTeam,user=request.user)
                    notification.save()
                return redirect('portal:index')
            else:
                newTeam = Team.objects.create(team_head=request.user,team_name=form.cleaned_data['team_name'],tournament='CS')
                uniqueUser = Profile.objects.get(id=request.user.id)
                uniqueUser.status_CS = 1

                uniqueUser.save()
                newTeam.save()
                uniqueUser.team_cs = newTeam
                return redirect('portal:CSView',team_id = newTeam.id)
            return render(request, self.template_name,{'form':form,'profiles':profiles,'players':players})
        else:
            return render(request, self.template_name,{'form':form,'profiles':profiles,'players':players})

def CSView(request,team_id):
    template_name = 'portal/csgodash.html'
    form_class = PlayerForm
    form_class2 = DeleteTeamForm
    
    if request.method == "GET":
        team1 = Team.objects.get(id=team_id)
        notifications = TeamNotification.objects.filter(team=team1)
        form =form_class(None)
        team_head=None
        player1=None
        player2=None
        player3=None
        player4=None
        team_head_user = None
        user1 = None
        user2 = None
        user3 = None
        user4 = None
        team_head = Profile.objects.get(user=team1.team_head)
        team_head_user=User.objects.get(id=team1.team_head.id)
        if team1.player1!=None:
            user1 = User.objects.get(username=team1.player1)
            player1 = Profile.objects.get(user=user1)
            
        if team1.player2!=None:
            user2 = User.objects.get(username=team1.player2)
            player2 = Profile.objects.get(user=user2)
        if team1.player3!=None:
            user3 = User.objects.get(username=team1.player3)
            player3 = Profile.objects.get(user=user3)
        if team1.player4!=None:
            user4 = User.objects.get(username=team1.player4)
            player4 = Profile.objects.get(user=user4)
        
        '''form2=form_class(None)
        form3=form_class2(None)'''
        if notifications.count()==0:
            notifications=None
        return render(request, template_name,{'notifications':notifications,'team1':team1,'form':form,'team_head':team_head,'team_head_user':team_head_user,'player1':player1,'user1':user1,'player2':player2,'user2':user2,'player3':player3,'user3':user3,'player4':player4,'user4':user4})
    if request.method == "POST":
        team1 = Team.objects.get(id=team_id)
        notifications = TeamNotification.objects.filter(team=team1)
        if notifications.count()==0:
            notifications=None
        form =form_class(request.POST)
        '''form2=form_class(request.POST)
        form3=form_class2(request.POST)'''
        if form.is_valid():
            uniqueUser = User.objects.filter(username=form.cleaned_data['player'])
            if uniqueUser.count()!=0:
                user1 = User.objects.get(username=form.cleaned_data['player'])
                uniqueUser = Profile.objects.get(user=user1)
                if uniqueUser.status_CS==0:
                    if team1.player1 == None:
                        team1.player1 = form.cleaned_data['player']
                        uniqueUser.status_CS = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player2 == None:
                        team1.player2 = form.cleaned_data['player']
                        uniqueUser.status_CS = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player3 == None:
                        team1.player3 = form.cleaned_data['player']
                        uniqueUser.status_CS = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player4 == None:
                        team1.player4 = form.cleaned_data['player']
                        uniqueUser.status_CS = 1
                        uniqueUser.save()
                        team1.save()
                
        
        team_head=None
        player1=None
        player2=None
        player3=None
        player4=None
        team_head_user = None
        user1 = None
        user2 = None
        user3 = None
        user4 = None
        team_head = Profile.objects.get(user=team1.team_head)
        team_head_user=User.objects.get(id=team1.team_head.id)
        if team1.player1!=None:
            user1 = User.objects.get(username=team1.player1)
            player1 = Profile.objects.get(user=user1)           
        if team1.player2!=None:
            user2 = User.objects.get(username=team1.player2)
            player2 = Profile.objects.get(user=user2)
        if team1.player3!=None:
            user3 = User.objects.get(username=team1.player3)
            player3 = Profile.objects.get(user=user3)
        if team1.player4!=None:
            user4 = User.objects.get(username=team1.player4)
            player4 = Profile.objects.get(user=user4)
        return render(request, template_name,{'notifications':notifications,'team1':team1,'form':form,'team_head':team_head,'team_head_user':team_head_user,'player1':player1,'user1':user1,'player2':player2,'user2':user2,'player3':player3,'user3':user3,'player4':player4,'user4':user4})

def CSTeamConfirmView(request,team_id,user_id):
    team_id1 = team_id
    if request.method == "GET" and Profile.objects.get(id=user_id).status_CS==0:
        uniqueTeam = Team.objects.get(id=team_id)
        user1 = User.objects.get(id=user_id)
        if uniqueTeam.player1 == None:
            uniqueTeam.player1 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_CS = 1
            uniqueUser.team_cs=uniqueTeam
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player2 == None:
            uniqueTeam.player2 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_CS = 1
            uniqueUser.team_cs=uniqueTeam
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player3 == None:
            uniqueTeam.player3 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_CS = 1
            uniqueUser.team_cs=uniqueTeam
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player4 == None:
            uniqueTeam.player4 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_CS = 1
            uniqueUser.team_cs=uniqueTeam
            uniqueUser.save()
            uniqueTeam.save()
        notification = TeamNotification.objects.get(team=uniqueTeam,user=user1)
        notification.delete()
    return redirect('portal:CSView',team_id = team_id1)


class DOTA(View):
    template_name = 'portal/DOTA.html'
    form_class = TeamForm
    def get(self,request):
        players = User.objects.all()
        profiles = Profile.objects.get(id=request.user.id)
        form = self.form_class(None)
        return render(request, self.template_name,{'form':form,'profiles':profiles, 'players':players})
    def post(self,request):
        form = self.form_class(request.POST)
        profiles = Profile.objects.get(id=request.user.id)
        players = User.objects.all()
        if form.is_valid():
            uniqueTeam = Team.objects.filter(team_name=form.cleaned_data['team_name'],tournament='DOTA')
            if uniqueTeam.count() > 0:
                uniqueTeam = Team.objects.get(team_name=form.cleaned_data['team_name'],tournament='DOTA')
                if TeamNotification.objects.filter(team=uniqueTeam,user=request.user).count()==0:
                    notification = TeamNotification.objects.create(team=uniqueTeam,user=request.user)
                    notification.save()
                return redirect('portal:index')
            else:
                newTeam = Team.objects.create(team_head=request.user,team_name=form.cleaned_data['team_name'],tournament='DOTA')
                uniqueUser = Profile.objects.get(id=request.user.id)
                uniqueUser.status_DOTA = 1
                uniqueUser.save()
                newTeam.save()
                return redirect('portal:DOTAView',team_id = newTeam.id)
            return render(request, self.template_name,{'form':form,'profiles':profiles,'players':players})
        else:
            return render(request, self.template_name,{'form':form,'profiles':profiles,'players':players})

def DOTAView(request,team_id):
    template_name = 'portal/dotadash.html'
    form_class = PlayerForm
    form_class2 = DeleteTeamForm
    
    if request.method == "GET":
        team1 = Team.objects.get(id=team_id)
        notifications = TeamNotification.objects.filter(team=team1)
        form =form_class(None)
        '''form2=form_class(None)
        form3=form_class2(None)'''
        if notifications.count()==0:
            notifications=None
        return render(request, template_name,{'notifications':notifications,'team1':team1,'form':form})
    if request.method == "POST":
        team1 = Team.objects.get(id=team_id)
        notifications = TeamNotification.objects.filter(team=team1)
        if notifications.count()==0:
            notifications=None
        form =form_class(request.POST)
        '''form2=form_class(request.POST)
        form3=form_class2(request.POST)'''
        if form.is_valid():
            uniqueUser = User.objects.filter(username=form.cleaned_data['player'])
            if uniqueUser.count()!=0:
                user1 = User.objects.get(username=form.cleaned_data['player'])
                uniqueUser = Profile.objects.get(user=user1)
                if uniqueUser.status_DOTA==0:
                    if team1.player1 == None:
                        team1.player1 = form.cleaned_data['player']
                        uniqueUser.status_DOTA = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player2 == None:
                        team1.player2 = form.cleaned_data['player']
                        uniqueUser.status_DOTA = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player3 == None:
                        team1.player3 = form.cleaned_data['player']
                        uniqueUser.status_DOTA = 1
                        uniqueUser.save()
                        team1.save()
                    elif team1.player4 == None:
                        team1.player4 = form.cleaned_data['player']
                        uniqueUser.status_DOTA = 1
                        uniqueUser.save()
                        team1.save()
                
        return render(request, template_name,{'notifications':notifications,'team1':team1,'form':form})

def DOTATeamConfirmView(request,team_id,user_id):
    team_id1 = team_id
    if request.method == "GET" and Profile.objects.get(id=user_id).status_DOTA==0:
        uniqueTeam = Team.objects.get(id=team_id)
        user1 = User.objects.get(id=user_id)
        if uniqueTeam.player1 == None:
            uniqueTeam.player1 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_DOTA = 1
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player2 == None:
            uniqueTeam.player2 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_DOTA = 1
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player3 == None:
            uniqueTeam.player3 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_DOTA = 1
            uniqueUser.save()
            uniqueTeam.save()
        elif uniqueTeam.player4 == None:
            uniqueTeam.player4 = user1.username
            uniqueUser = Profile.objects.get(id=user1.id)
            uniqueUser.status_DOTA = 1
            uniqueUser.save()
            uniqueTeam.save()
        notification = TeamNotification.objects.get(team=uniqueTeam,user=user1)
        notification.delete()
    if request.method == "GET" and Profile.objects.get(id=user_id).status_DOTA==1:
        uniqueTeam = Team.objects.get(id=team_id)
        user1 = User.objects.get(id=user_id)
        notification = TeamNotification.objects.get(team=uniqueTeam,user=user1)
        notification.delete()
		
    return redirect('portal:DOTAView',team_id = team_id1)


def DeleteTeam(request, team_id):
    team1 = Team.objects.get(id=team_id)
    if team1.player1 != None:
        team1.player1 = None
        user1=User.objects.get(username=team1.player1)
        uniqueUser = Profile.objects.get(user=user1)
        if team1.tournament=="CS":
            uniqueUser.status_CS = 0
        if team1.tournament=="DOTA":
            uniqueUser.status_DOTA = 0
        uniqueUser.save()

    if team1.player2 != None:
        team1.player2 = None
        user1=User.objects.get(username=team1.player2)
        uniqueUser = Profile.objects.get(user=user1)
        if team1.tournament=="CS":
            uniqueUser.status_CS = 0
        if team1.tournament=="DOTA":
            uniqueUser.status_DOTA = 0
        uniqueUser.save()

    if team1.player3 != None:
        team1.player3 = None
        user1=User.objects.get(username=team1.player3)
        uniqueUser = Profile.objects.get(user=user1)
        if team1.tournament=="CS":
            uniqueUser.status_CS = 0
        if team1.tournament=="DOTA":
            uniqueUser.status_DOTA = 0
        uniqueUser.save()

    if team1.player4 != None:
        team1.player4 = None
        user1=User.objects.get(username=team1.player4)
        uniqueUser = Profile.objects.get(user=user1)
        if team1.tournament=="CS":
            uniqueUser.status_CS = 0
        if team1.tournament=="DOTA":
            uniqueUser.status_DOTA = 0
        uniqueUser.save()

    user1=User.objects.get(username=team1.team_head.username)
    uniqueUser = Profile.objects.get(user=user1)
    if team1.tournament=="CS":
        uniqueUser.status_CS = 0
    if team1.tournament=="DOTA":
        uniqueUser.status_DOTA = 0
    uniqueUser.save()
    team1.delete()
    return redirect('portal:index')


def RemovePlayer(request,team_id,player_no):
    team_id1=team_id
    player_no=int(player_no)
    if request.method=="GET":
        team1 = Team.objects.get(id=team_id)
        user1=None
        if player_no==1:
            user1 = User.objects.get(username=team1.player1)
        elif player_no==2:
            user1 = User.objects.get(username=team1.player2)
        elif player_no==3:
            user1 = User.objects.get(username=team1.player3)
        elif player_no==4:
            user1 = User.objects.get(username=team1.player4)
            
        if player_no == 1:
            team1.player1 = None
            uniqueUser = Profile.objects.get(user=user1)
            if team1.tournament=="CS":
                uniqueUser.status_CS = 0
            if team1.tournament=="DOTA":
                uniqueUser.status_DOTA = 0
            uniqueUser.save()
            team1.save()
        elif player_no == 2:
            team1.player2 = None
            uniqueUser = Profile.objects.get(user=user1)
            if team1.tournament=="CS":
                uniqueUser.status_CS = 0
            if team1.tournament=="DOTA":
                uniqueUser.status_DOTA = 0
            uniqueUser.save()
            team1.save()
        elif player_no == 3:
            team1.player3 = None
            uniqueUser = Profile.objects.get(user=user1)
            if team1.tournament=="CS":
                uniqueUser.status_CS = 0
            if team1.tournament=="DOTA":
                uniqueUser.status_DOTA = 0
            uniqueUser.save()
            team1.save()
        elif player_no == 4:
            team1.player4 = None
            uniqueUser = Profile.objects.get(user=user1)
            if team1.tournament=="CS":
                uniqueUser.status_CS = 0
            if team1.tournament=="DOTA":
                uniqueUser.status_DOTA = 0
            uniqueUser.save()
            team1.save()
            
    team1 = Team.objects.get(id=team_id1)
    if team1.tournament == "CS":
        return redirect('portal:CSView',team_id = team_id1)
    if team1.tournament == "DOTA":
        return redirect('portal:DOTAView',team_id = team_id1)
    
    

def logout_view(request):
    logout(request)
    template_name = 'portal/before_login.html'
    return render(request, template_name)

def home(request):
    template_name = 'portal/index.html'
    return render(request, template_name)