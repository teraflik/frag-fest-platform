from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from portal.models import Tournament, Team, Profile
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email id.',
                             widget=forms.TextInput(attrs={'placeholder': 'you@example.com', 'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    subscribe = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    agree_terms = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'subscribe', 'agree_terms')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a unique username', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'form-control'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'location', 'steam_id',)
        widgets = {
            'steam_id': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class forgetpass(forms.Form):
    usernamee = forms.CharField(label='Username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'enter username', 'class':'form-control'}))
    
class TeamForm(forms.ModelForm):
     class Meta:
         model = Team
         fields = ['team_name']

class PlayerForm(forms.Form):
    player = forms.CharField(label='player', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Player', 'class':'form-control'}))

class DeleteTeamForm(forms.Form):
    team = forms.CharField(label='team', max_length=100, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Team Name', 'class': 'forms.Form-control'}))
