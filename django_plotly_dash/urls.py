from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import routes, layout, dependencies, update, main_view

app_name = "django_plotly_dash"

urlpatterns = [
    path('<slug:id>_dash-routes', routes, name="routes"),
    path('<slug:id>_dash-layout', layout, name="layout"),
    path('<slug:id>_dash-dependencies', dependencies, name="dependencies"),
    path('<slug:id>_dash-update-component', csrf_exempt(update), name="update-component"),

    path('<slug:id>', main_view, name="main"),
    ]

