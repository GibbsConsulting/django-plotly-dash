'''
Template tags for exposing dash applications in Django templates

Copyright (c) 2018 Gibbs Consulting and others - see CONTRIBUTIONS.md

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

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

@register.simple_tag()
def plotly_app_identifier(name=None, slug=None, da=None, postfix=None):
    'Return a slug-friendly identifier'
    if name is not None:
        da, app = DashApp.locate_item(name, stateless=True)

    if slug is not None:
        da, app = DashApp.locate_item(slug, stateless=False)

    if not app:
        app = da.as_dash_instance()

    slugified_id = app.slugified_id()

    if postfix:
        return "%s-%s" %(slugified_id, postfix)
    return slugified_id

@register.simple_tag()
def plotly_class(name=None, slug=None, da=None, prefix=None, postfix=None, template_type=None):
    'Return a string of space-separated class names'

    if name is not None:
        da, app = DashApp.locate_item(name, stateless=True)

    if slug is not None:
        da, app = DashApp.locate_item(slug, stateless=False)

    if not app:
        app = da.as_dash_instance()

    return app.extra_html_properties(prefix=prefix,
                                     postfix=postfix,
                                     template_type=template_type)
