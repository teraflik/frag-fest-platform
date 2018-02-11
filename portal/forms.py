from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from portal.models import Tournament, Team, Profile
from django.forms import Form, ModelForm, TextInput

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    subscribe = forms.BooleanField(required=False)
    agree_terms = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'subscribe', 'agree_terms')
        widgets = {
            'username': TextInput(attrs={'placeholder': 'Username'}),
            'email': TextInput(attrs={'placeholder': 'Email'}),
            'first_name': TextInput(attrs={'placeholder': 'First name'}),
            'last_name': TextInput(attrs={'placeholder': 'Last name'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)
        widgets = {
            'username': TextInput(attrs={'class':'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'location', 'steam_id',)
        widgets = {
            'steam_id': TextInput(attrs={'class': 'form-control'}),
            'location': TextInput(attrs={'class': 'form-control'}),
        }

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
