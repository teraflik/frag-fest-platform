from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Tournament,Team,Profile
from django.forms import Form, ModelForm, TextInput

class UserForm(ModelForm):
    password = forms.CharField(label='password', required=True, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    
    class Meta:
        model = User
        password = forms.CharField(label='password', required=True, widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'}))
        fields = ['username','email','password','first_name','last_name']
        widgets = {
            'username': TextInput(attrs={'placeholder': 'Username'}),
            'email': TextInput(attrs={'placeholder': 'Email'}),
            'first_name': TextInput(attrs={'placeholder': 'First name'}),
            'last_name': TextInput(attrs={'placeholder': 'Last name'}) ,
        }
        labels = {
                'email' : 'email',
                'password': 'password',
            }

class UpdateForm(Form):
    username = forms.CharField(label='username', max_length=100, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'class': 'form-control'}))


class TournamentForm(ModelForm):   
    class Meta:
        model = Tournament
        fields = ['tournament_name','tournament_date','no_of_players']
        
class subscriptionform(Form):
    is_subscribe = forms.BooleanField(initial=True)

class ProfileForm(Form):
    steam_id = forms.CharField(label='steam_id', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Steam ID', 'class':'form-control'}))
    location = forms.CharField(label='location', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Location', 'class':'form-control'}))

class changepass(Form):
    new_pass = forms.CharField(label='New Password', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'New Password', 'class':'form-control'}))

class forgetpass(Form):
    usernamee = forms.CharField(label='Username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'enter username', 'class':'form-control'}))
    
class TeamForm(ModelForm):
     class Meta:
         model = Team
         fields = ['team_name']

class PlayerForm(Form):
    player = forms.CharField(label='player', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Player', 'class':'form-control'}))

class DeleteTeamForm(Form):
    team = forms.CharField(label='team', max_length=100, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Team Name', 'class': 'form-control'}))
