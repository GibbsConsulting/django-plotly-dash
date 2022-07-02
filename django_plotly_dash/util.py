'''
Utility functions

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
import json
import uuid


from plotly.io._json import config
from plotly.utils import PlotlyJSONEncoder

from _plotly_utils.optional_imports import get_module


from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.module_loading import import_string


def _get_settings():
    try:
        the_settings = settings.PLOTLY_DASH
    except AttributeError:
        the_settings = None

    return the_settings if the_settings else {}

def pipe_ws_endpoint_name():
    'Return the endpoint for pipe websocket connections'
    return _get_settings().get('ws_route', 'dpd/ws/channel')

def dpd_http_endpoint_root():
    'Return the root of the http endpoint for direct insertion of pipe messages'
    return _get_settings().get('http_route', 'dpd/views')

def http_endpoint(stem):
    'Form the http endpoint for a specific stem'
    return "^%s/%s/$" % (dpd_http_endpoint_root(), stem)

def insert_demo_migrations():
    'Check settings and report if objects for demo purposes should be inserted during migration'

    return _get_settings().get('insert_demo_migrations', False)

def http_poke_endpoint_enabled():
    'Return true if the http endpoint is enabled through the settings'
    return _get_settings().get('http_poke_enabled', True)

def cache_timeout_initial_arguments():
    'Return cache timeout, in seconds, for initial arguments'
    return _get_settings().get('cache_timeout_initial_arguments', 60)

def initial_argument_location():
    'Return True if cache to be used for setting and getting initial arguments, or False for a session'

    setget_location = _get_settings().get('cache_arguments', True)

    return setget_location

def store_initial_arguments(request, initial_arguments=None):
    'Store initial arguments, if any, and return a cache identifier'

    if initial_arguments is None:
        return None

    # convert to dict is json string
    if isinstance(initial_arguments, str):
        initial_arguments = json.loads(initial_arguments)

    # Generate a cache id
    cache_id = "dpd-initial-args-%s" % str(uuid.uuid4()).replace('-', '')

    # Store args in json form in cache
    if initial_argument_location():
        cache.set(cache_id, initial_arguments, cache_timeout_initial_arguments())
    else:
        request.session[cache_id] = initial_arguments

    return cache_id

def get_initial_arguments(request, cache_id=None):
    'Extract initial arguments for the dash app'

    if cache_id is None:
        return None

    if initial_argument_location():
        return cache.get(cache_id)

    return request.session[cache_id]

def static_asset_root():
    return _get_settings().get('static_asset_root','dpd/assets')

def full_asset_path(module_name, asset_path):
    path_contrib = "%s/%s/%s" %(static_asset_root(),
                                "/".join(module_name.split(".")),
                                asset_path)
    return path_contrib

def static_asset_path(module_name, asset_path):
    return static_path(full_asset_path(module_name, asset_path))

def serve_locally():
    return _get_settings().get('serve_locally', False)

def static_path(relative_path):
    try:
        static_url = settings.STATIC_URL
    except:
        static_url = '/static/'
    return "%s%s" %(static_url, relative_path)

def stateless_app_lookup_hook():
    'Return a function that performs lookup for aa stateless app, given its name, or returns None'

    func_name = _get_settings().get('stateless_loader', None)
    if func_name:
        func = import_string(func_name)
        return func

    # Default is no additional lookup
    return lambda _: None


class DjangoPlotlyJSONEncoder(PlotlyJSONEncoder):
    """Augment the PlotlyJSONEncoder class with Django delayed processing"""
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super().default(obj)


def to_json_django_plotly(plotly_object, pretty=False, engine=None):
    """
    Convert a plotly/Dash object to a JSON string representation

    Parameters
    ----------
    plotly_object:
        A plotly/Dash object represented as a dict, graph_object, or Dash component

    pretty: bool (default False)
        True if JSON representation should be pretty-printed, False if
        representation should be as compact as possible.

    engine: str (default None)
        The JSON encoding engine to use. One of:
          - "json" for an engine based on the built-in Python json module
          - "orjson" for a faster engine that requires the orjson package
          - "auto" for the "orjson" engine if available, otherwise "json"
        If not specified, the default engine is set to the current value of
        plotly.io.json.config.default_engine.

    Returns
    -------
    str
        Representation of input object as a JSON string

    See Also
    --------
    to_json : Convert a plotly Figure to JSON with validation
    """
    orjson = get_module("orjson", should_load=True)

    # Determine json engine
    if engine is None:
        engine = config.default_engine

    if engine == "auto":
        if orjson is not None:
            engine = "orjson"
        else:
            engine = "json"
    elif engine not in ["orjson", "json"]:
        raise ValueError("Invalid json engine: %s" % engine)

    modules = {
        "sage_all": get_module("sage.all", should_load=False),
        "np": get_module("numpy", should_load=False),
        "pd": get_module("pandas", should_load=False),
        "image": get_module("PIL.Image", should_load=False),
    }

    # Dump to a JSON string and return
    # --------------------------------
    if engine == "json":
        opts = {}
        if pretty:
            opts["indent"] = 2
        else:
            # Remove all whitespace
            opts["separators"] = (",", ":")

        return json.dumps(plotly_object, cls=DjangoPlotlyJSONEncoder, **opts)
    elif engine == "orjson":
        JsonConfig.validate_orjson()
        opts = orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY

        if pretty:
            opts |= orjson.OPT_INDENT_2

        # Plotly
        try:
            plotly_object = plotly_object.to_plotly_json()
        except AttributeError:
            pass

        # Try without cleaning
        try:
            return orjson.dumps(plotly_object, option=opts).decode("utf8")
        except TypeError:
            pass

        cleaned = clean_to_json_compatible(
            plotly_object,
            numpy_allowed=True,
            datetime_allowed=True,
            modules=modules,
        )
        return orjson.dumps(cleaned, option=opts).decode("utf8")


import plotly.io.json
plotly.io.json.to_json_plotly = to_json_django_plotly
