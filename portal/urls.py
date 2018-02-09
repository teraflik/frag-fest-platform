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

app_name = 'portal'

urlpatterns = [ 
    # /portal/
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^home/$', views.home, name='home'),
    #url(r'^$',views.index,name='index')
    #url(r'^base/$',views.BaseView,name='base'),
    url(r'^profile/$', views.ProfileView, name='profile'), 
    url(r'^change_password/$', views.change_password, name='change_password'), 
    url(r'^login/$', auth_views.login, {'template_name': 'portal/login.html'}, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^teams/$', views.TeamView.as_view(), name='teams'),
    url(r'^dashboard/', views.dashboard.as_view(), name='dashboard'),
    url(r'^CSConfirm123/2/(?P<team_id>\d+)/4/21/(?P<user_id>\d+)/32/$', views.CSTeamConfirmView, name='CSTeamConfirmView'),
    url(r'^RemovePlayer123/32/21/(?P<team_id>\d+)/4/21/(?P<user_id>\d+)/5/$', views.RemovePlayer, name='RemovePlayer'),
    url(r'^DeleteTeam123/32/21/(?P<team_id>\d+)/$', views.DeleteTeam, name='DeleteTeam'),
]
