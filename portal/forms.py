from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django import forms
from portal.models import MyUser, Team, Profile
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

class SignUpForm(UserCreationForm):
    """Class to render the signup form for the signup view."""
    email = forms.EmailField(max_length=254, 
                                required=True, 
                                help_text='Enter a valid email id. Must be unique',
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'you@example.com', 
                                    'class': 'form-control'}))
    password1 = forms.CharField(label="Password",
                                strip=False,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password",
                                strip=False,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control'}),
                                help_text="Enter the same password as above, for verification.")
    subscribe = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    agree_terms = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    
    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'subscribe', 'agree_terms')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': '(Optional)', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': '(Optional)', 'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    """Login Form inherited to add form-control class."""

    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class':'form-control'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

class ProfileForm(forms.ModelForm):
    """Update Profile related fields on edit profile page."""
    class Meta:
        model = Profile
        fields = ('avatar', 'username', 'location', 'steam_id',)
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username does not need to be unique.', 'class': 'form-control'}),
            'steam_id': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class forgetpass(forms.Form):
    usernamee = forms.CharField(label='Username', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'enter username', 'class':'form-control'}))
    
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', 'info')

class PlayerForm(forms.Form):
    player = forms.CharField(label='player', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Player', 'class':'form-control'}))

class DeleteTeamForm(forms.Form):
    team = forms.CharField(label='team', max_length=100, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Team Name', 'class': 'forms.Form-control'}))
