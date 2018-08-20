app_name = 'django_app'

from django.urls import path, re_path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views
from . import dash_apps
from .dash_apps import dash_example1

urlpatterns = [

   url('^%s$' %(dash_apps.dashboard_name1), views.dashboard_name1, name="dash_example1"),

   ]
