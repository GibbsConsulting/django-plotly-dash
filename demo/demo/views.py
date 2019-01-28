'''
Example view generating non-trivial content
'''

from django.shortcuts import render

#pylint: disable=unused-argument

def dash_example_1_view(request, template_name="demo_six.html", **kwargs):
    'Example view that inserts content into the dash context passed to the dash application'

    context = {}

    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['django_to_dash_context'] = "I am Dash receiving context from Django"
    request.session['django_plotly_dash'] = dash_context

    return render(request, template_name=template_name, context=context)

def session_state_view(request, template_name, **kwargs):
    'Example view that exhibits the use of sessions to store state'

    session = request.session

    demo_count = session.get('django_plotly_dash', {})

    ind_use = demo_count.get('ind_use', 0)
    ind_use += 1
    demo_count['ind_use'] = ind_use

    context = {'ind_use' : ind_use}

    session['django_plotly_dash'] = demo_count

    return render(request, template_name=template_name, context=context)
