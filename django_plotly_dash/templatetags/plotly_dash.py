from django import template

register = template.Library()

from django_plotly_dash.dash_wrapper import get_app_by_name

@register.inclusion_tag("django_plotly_dash/plotly_item.html", takes_context=True)
def plotly_item(context, app_name):

    app = get_app_by_name(app_name)
    url = app.base_url()

    return locals()
