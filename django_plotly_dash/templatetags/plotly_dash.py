from django import template
from django.shortcuts import get_object_or_404

register = template.Library()

from django_plotly_dash.models import DashApp
from django_plotly_dash.util import pipe_ws_endpoint_name

ws_default_url = "/%s" % pipe_ws_endpoint_name()

@register.inclusion_tag("django_plotly_dash/plotly_item.html", takes_context=True)
def plotly_app(context, name=None, slug=None, da=None, ratio=0.1, use_frameborder=False):

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

    app = None

    if name is not None:
        da, app = DashApp.locate_item(name, stateless=True)

    if slug is not None:
        da, app = DashApp.locate_item(slug, stateless=False)

    if not app:
        app = da.as_dash_instance()

    return locals()

@register.inclusion_tag("django_plotly_dash/plotly_messaging.html", takes_context=True)
def plotly_message_pipe(context, url=None):
    global ws_default_url
    url = url and url or ws_default_url
    return locals()
