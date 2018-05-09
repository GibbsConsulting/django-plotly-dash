from django import template

register = template.Library()

from django_plotly_dash.dash_wrapper import get_or_form_app

@register.inclusion_tag("django_plotly_dash/plotly_item.html", takes_context=True)
def plotly_item(context, app_name):

    app = get_or_form_app(app_name, app_name)

    return locals()
