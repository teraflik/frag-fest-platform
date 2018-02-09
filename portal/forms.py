from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Player,Tournament,Team,Profile
from django.forms import ModelForm, TextInput

class UserForm(forms.ModelForm):
    #username = forms.CharField(label='username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username*'}))
    #email = forms.EmailField(label='email', required=True, widget=forms.TextInput(attrs={'placeholder': 'Email*'}))
    password = forms.CharField(label='password', required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password*'}))
    #first_name = forms.CharField(label='first_name',required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name*'}))
    #last_name = forms.CharField(label='last_name',required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name*'}))
    
    
    class Meta:
        model = User
        password = forms.CharField(label='password', required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password*'}))
        fields = ['username','email','password','first_name','last_name']
        widgets = {
            'username': TextInput(attrs={'placeholder': 'Username*'}),
            'email': TextInput(attrs={'placeholder': 'Email*'}),
            'first_name': TextInput(attrs={'placeholder': 'First name*'}),
            'last_name': TextInput(attrs={'placeholder': 'Last name*'}) ,
        }
        labels = {
                'email' : 'email',
                'password': 'password',
            }

class UpdateForm(forms.Form):
    username = forms.CharField(label='username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username*'}))
    first_name = forms.CharField(label='first_name',required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name*'}))
    last_name = forms.CharField(label='last_name',required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name*'}))


class TournamentForm(forms.ModelForm):   
    class Meta:
        model = Tournament
        fields = ['tournament_name','tournament_date','no_of_players']
        
class subscriptionform(forms.Form):
    is_subscribe = forms.BooleanField(initial=True)

class ProfileForm(forms.Form):
    steam_id = forms.CharField(label='steam_id', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Steam ID'}))
    location = forms.CharField(label='location', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Location'}))

class changepass(forms.Form):
    new_pass = forms.CharField(label='New Password', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'New Password'}))

class forgetpass(forms.Form):
    usernamee = forms.CharField(label='Username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'enter username'}))
    
class TeamForm(forms.ModelForm):
     class Meta:
         model = Team
         fields = ['team_name']

class PlayerForm(forms.Form):
    player = forms.CharField(label='player', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Player'}))

class DeleteTeamForm(forms.Form):
    team = forms.CharField(label='team', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Team Name'}))
