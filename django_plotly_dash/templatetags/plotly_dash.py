from django import template

register = template.Library()

from django_plotly_dash.models import DashApp

@register.inclusion_tag("django_plotly_dash/plotly_item.html", takes_context=True)
def plotly_item(context, app_name):

    app = DashApp.get_app_instance(app_name)

    return locals()
