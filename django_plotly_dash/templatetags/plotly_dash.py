'Template tags for exposing dash applications in Django templates'

# pylint: disable=too-many-arguments, unused-variable, unused-argument

from django import template

from django_plotly_dash.models import DashApp
from django_plotly_dash.util import pipe_ws_endpoint_name

register = template.Library()

ws_default_url = "/%s" % pipe_ws_endpoint_name()

@register.inclusion_tag("django_plotly_dash/plotly_app.html", takes_context=True)
def plotly_app(context, name=None, slug=None, da=None, ratio=0.1, use_frameborder=False):
    'Insert a dash application using a html iframe'

    fbs = '1' if use_frameborder else '0'

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
    'Insert script for providing background websocket connection'
    url = url if url else ws_default_url
    return locals()
