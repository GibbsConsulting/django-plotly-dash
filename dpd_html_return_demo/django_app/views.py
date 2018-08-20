# Django related imports:
from django.shortcuts import render

# Dash related imports:
from .dash_apps import dash_example1

from django_plotly_dash.views import create_Dash_html

def dashboard_name1(request):
    print("Function dashboard_name1.")
    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['django_to_dash_context'] = "I am Dash receiving context from Django"
    request.session['django_plotly_dash'] = dash_context

    # create the Dash html, which is saved to request.session['dash_content']
   # the 'create_Dash_html' function decides whether it needs to redirect to the "main_view" in views.py, which then redirects back to
   # this view.
    http_redirect = create_Dash_html(request, dash_example1)
    if http_redirect: # Ideally, this function would redirect straight to main_view but I can't quite figure out why it can't
        return http_redirect

    return render(request, 'django_app/dash_page1.html', context={'dash_content': request.session['dash_content']})
