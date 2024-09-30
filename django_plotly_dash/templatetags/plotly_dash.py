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

# pylint: disable=too-many-arguments, unused-variable, unused-argument, possibly-unused-variable

from django import template

from django.contrib.sites.shortcuts import get_current_site

from django_plotly_dash.models import DashApp
from django_plotly_dash.util import pipe_ws_endpoint_name, store_initial_arguments


register = template.Library()


ws_default_url = "/%s" % pipe_ws_endpoint_name()


SANDBOX_SETTINGS = ["allow-downloads",
                    "allow-scripts",
                    "allow-same-origin",
                    "allow-modals",
                    "allow-popups",
                    "allow-popups-to-escape-sandbox",
                    ]


SANDBOX_STRING = " ".join(SANDBOX_SETTINGS)


def _locate_daapp(name, slug, da, cache_id=None):

    app = None

    if name is not None:
        da, app = DashApp.locate_item(name, stateless=True, cache_id=cache_id)

    if slug is not None:
        da, app = DashApp.locate_item(slug, stateless=False, cache_id=cache_id)

    if not app:
        app = da.as_dash_instance()

    return da, app


@register.inclusion_tag("django_plotly_dash/plotly_app.html", takes_context=True)
def plotly_app(context, name=None, slug=None, da=None, ratio=0.1,
               use_frameborder=False, initial_arguments=None,
               height=None):
    'Insert a dash application using a html iframe'

    fbs = '1' if use_frameborder else '0'

    if height is None:
        dstyle = """
        position: relative;
        padding-bottom: %s%%;
        height: 0;
        overflow:hidden;
        """ % (ratio*100)
    else:
        dstyle = f"""
        position: relative;
        height: {height};
        overflow:hidden;
        """

    istyle = """
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    """

    cache_id = store_initial_arguments(context['request'], initial_arguments)

    da, app = _locate_daapp(name, slug, da, cache_id=cache_id)

    sandbox_settings = SANDBOX_STRING
    
    return locals()


@register.inclusion_tag("django_plotly_dash/plotly_app_bootstrap.html", takes_context=True)
def plotly_app_bootstrap(context, name=None, slug=None, da=None, aspect="4by3", initial_arguments=None):
    'Insert a dash application using a html iframe'

    valid_ratios = ['21by9',
                    '16by9',
                    '4by3',
                    '1by1',
                    ]

    if aspect not in valid_ratios:
        raise ValueError("plotly_app_bootstrap requires a valid aspect ratio from %s, but was supplied %s" % (str(valid_ratios),
                                                                                                              aspect))

    cache_id = store_initial_arguments(context['request'], initial_arguments)

    da, app = _locate_daapp(name, slug, da, cache_id=cache_id)

    sandbox_settings = SANDBOX_STRING
    
    return locals()


@register.simple_tag(takes_context=True)
def plotly_header(context):
    'Insert placeholder for django-plotly-dash header content'
    return context.request.dpd_content_handler.header_placeholder


@register.simple_tag(takes_context=True)
def plotly_footer(context):
    'Insert placeholder for django-plotly-dash footer content'
    return context.request.dpd_content_handler.footer_placeholder


@register.inclusion_tag("django_plotly_dash/plotly_direct.html", takes_context=True)
def plotly_direct(context, name=None, slug=None, da=None):
    'Direct insertion of a Dash app'

    da, app = _locate_daapp(name, slug, da)

    view_func = app.locate_endpoint_function()

    # Load embedded holder inserted by middleware
    eh = context.request.dpd_content_handler.embedded_holder

    # Need to add in renderer launcher
    renderer_launcher = '<script id="_dash-renderer" type="application/javascript">var renderer = new DashRenderer();</script>'

    app.set_embedded(eh)
    try:
        resp = view_func()
    finally:
        eh.add_scripts(renderer_launcher)
        app.exit_embedded()

    return locals()


@register.inclusion_tag("django_plotly_dash/plotly_messaging.html", takes_context=True)
def plotly_message_pipe(context, url=None):
    'Insert script for providing background websocket connection'
    url = url if url else ws_default_url
    return locals()


@register.simple_tag()
def plotly_app_identifier(name=None, slug=None, da=None, postfix=None):
    'Return a slug-friendly identifier'

    da, app = _locate_daapp(name, slug, da)

    slugified_id = app.slugified_id()

    if postfix:
        return "%s-%s" %(slugified_id, postfix)
    return slugified_id


@register.simple_tag()
def plotly_class(name=None, slug=None, da=None, prefix=None, postfix=None, template_type=None):
    'Return a string of space-separated class names'

    da, app = _locate_daapp(name, slug, da)

    return app.extra_html_properties(prefix=prefix,
                                     postfix=postfix,
                                     template_type=template_type)


@register.simple_tag(takes_context=True)
def site_root_url(context):
    'Provide the root url of the demo site'
    current_site_url = get_current_site(context.request)
    return current_site_url.domain
