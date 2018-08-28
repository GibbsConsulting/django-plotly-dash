'''
Example view generating non-trivial content
'''

from django.shortcuts import render

def dash_example_1_view(request, template_name="demo_six.html",**kwargs):
    
    context = {}
    
    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['django_to_dash_context'] = "I am Dash receiving context from Django"
    request.session['django_plotly_dash'] = dash_context

    return render(request, template_name=template_name, context=context)
