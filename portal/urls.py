"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .forms import LoginForm
from . import views

app_name = 'portal'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^resend_verification/$', views.resend_verification, name='resend_verification'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^login/$', auth_views.login, {'template_name': 'portal/login.html',
                                        'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^steam_connect/$', views.steam_connect, name='steam_connect'),
    url(r'^team/(?P<team_id>\d+)/$', views.SingleTeam, name='single_team'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^teams$', views.TeamListView.as_view(), name='team_list'),
    url(r'^all_games$', TemplateView.as_view(template_name="stat/other_games.html"), name='all_games'),
    url(r'^fifa$', TemplateView.as_view(template_name="stat/fifa.html"), name='fifa'),
    url(r'^csgo$', TemplateView.as_view(template_name="stat/csgo.html"), name='csgo'),
    url(r'^event$', TemplateView.as_view(template_name="stat/event.html"), name='event'),
    url(r'^schedule$', TemplateView.as_view(template_name="stat/schedule.html"), name='schedule'),
    url(r'^cs_matches$', TemplateView.as_view(template_name="stat/cs_matches.html"), name='cs_matches'),
    url(r'^organizers$', TemplateView.as_view(template_name="stat/organizers.html"), name='organizers'),
    url(r'^terms_and_conditions$', TemplateView.as_view(template_name="stat/terms.html"), name='terms'),
    url(r'^sponsors$', TemplateView.as_view(template_name="stat/sponsors.html"), name='sponsors'),
]
