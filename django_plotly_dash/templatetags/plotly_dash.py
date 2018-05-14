from django import template
from django.shortcuts import get_object_or_404

register = template.Library()

from django_plotly_dash.models import DashApp
from django_plotly_dash.dash_wrapper import get_stateless_by_name

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

    if name is not None:
        da = get_stateless_by_name(name)

    if slug is not None:
        da = get_object_or_404(DashApp,slug=slug)

    app = da.form_dash_instance()
    return locals()

