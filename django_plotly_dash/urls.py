from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import routes, layout, dependencies, update, main_view, component_suites

from .app_name import app_name, main_view_label

urlpatterns = [
    path('instance/<slug:id>_dash-routes', routes, name="routes"),
    path('instance/<slug:id>_dash-layout', layout, name="layout"),
    path('instance/<slug:id>_dash-dependencies', dependencies, name="dependencies"),
    path('instance/<slug:id>_dash-update-component', csrf_exempt(update), name="update-component"),
    path('instance/<slug:id>', main_view, name=main_view_label),
    path('instance/<slug:id>_dash-component-suites/<slug:component>/<resource>', component_suites, name='component-suites'),

    path('app/<slug:id>_dash-routes', routes, {'stateless':True}, name="app-routes"),
    path('app/<slug:id>_dash-layout', layout, {'stateless':True}, name="app-layout"),
    path('app/<slug:id>_dash-dependencies', dependencies, {'stateless':True}, name="app-dependencies"),
    path('app/<slug:id>_dash-update-component', csrf_exempt(update), {'stateless':True}, name="app-update-component"),
    path('app/<slug:id>', main_view, {'stateless':True}, name='app-%s'%main_view_label),
    path('app/<slug:id>_dash-component-suites/<slug:component>/<resource>', component_suites, {'stateless':True}, name='app-component-suites'),
    ]

