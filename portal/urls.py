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
from . import views
from portal.forms import LoginForm

app_name = 'portal'

urlpatterns = [ 
    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^home/$', views.home, name='home'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^login/$', auth_views.login, {'template_name': 'portal/login.html',
                                        'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^team/(?P<team_id>\d+)/$', views.SingleTeam, name='single_team'),
    url(r'^teams/$', views.TeamView.as_view(), name='teams'),
    url(r'^dashboard/', views.dashboard.as_view(), name='dashboard'),
    url(r'^CSConfirm123/2/(?P<team_id>\d+)/4/21/(?P<user_id>\d+)/32/$', views.CSTeamConfirmView, name='CSTeamConfirmView'),
    url(r'^RemovePlayer123/32/21/(?P<team_id>\d+)/4/21/(?P<user_id>\d+)/5/$', views.RemovePlayer, name='RemovePlayer'),
    url(r'^DeleteTeam123/32/21/(?P<team_id>\d+)/$', views.DeleteTeam, name='DeleteTeam'),
]
