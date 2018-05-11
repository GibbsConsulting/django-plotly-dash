from django import template

register = template.Library()

from django_plotly_dash.models import DashApp

@register.inclusion_tag("django_plotly_dash/plotly_item.html", takes_context=True)
def plotly_item(context, app_name, ratio=0.1, use_frameborder=False):

    fbs = use_frameborder and '1' or '0'

    dstyle = """
    position: relative;
    padding-bottom: %s%%;
    height: 0;
    overflow:hidden;
    """ % (ratio*100)

    istyle = """
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    """

    app = DashApp.get_app_instance(app_name)

    return locals()
