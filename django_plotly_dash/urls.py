'url routes for serving dash applications'

# pylint: disable = unused-import

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import routes, layout, dependencies, update, main_view, component_suites

from .app_name import app_name, main_view_label

urlpatterns = [
    path('instance/<slug:ident>_dash-routes', routes, name="routes"),
    path('instance/<slug:ident>_dash-layout', layout, name="layout"),
    path('instance/<slug:ident>_dash-dependencies', dependencies, name="dependencies"),
    path('instance/<slug:ident>_dash-update-component',
         csrf_exempt(update), name="update-component"),
    path('instance/<slug:ident>', main_view, name=main_view_label),
    path('instance/<slug:ident>_dash-component-suites/<slug:component>/<resource>',
         component_suites, name='component-suites'),

    path('app/<slug:ident>_dash-routes', routes, {'stateless':True}, name="app-routes"),
    path('app/<slug:ident>_dash-layout', layout, {'stateless':True}, name="app-layout"),
    path('app/<slug:ident>_dash-dependencies',
         dependencies, {'stateless':True}, name="app-dependencies"),
    path('app/<slug:ident>_dash-update-component',
         csrf_exempt(update), {'stateless':True}, name="app-update-component"),
    path('app/<slug:ident>', main_view, {'stateless':True}, name='app-%s'%main_view_label),
    path('app/<slug:ident>_dash-component-suites/<slug:component>/<resource>',
         component_suites, {'stateless':True}, name='app-component-suites'),
    ]
