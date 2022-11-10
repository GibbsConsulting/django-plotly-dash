'''
Collation of patches made to other python libraries, such as Dash itself.

If/when the patches are not needed they will be removed from this file.


Copyright (c) 2022 Gibbs Consulting and others - see CONTRIBUTIONS.md

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


from plotly.io._json import config, clean_to_json_compatible
from plotly.utils import PlotlyJSONEncoder

from _plotly_utils.optional_imports import get_module
from django.utils.encoding import force_str
from django.utils.functional import Promise


class DjangoPlotlyJSONEncoder(PlotlyJSONEncoder):
    """Augment the PlotlyJSONEncoder class with Django delayed processing"""
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super().default(obj)


def promise_clean_to_json_compatible(obj):

    if isinstance(obj, dict):
        return {promise_clean_to_json_compatible(k): promise_clean_to_json_compatible(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        if obj:
            return [promise_clean_to_json_compatible(v) for v in obj]

    if isinstance(obj, Promise):
        return force_str(obj)

    #try:
    #    return obj.to_plotly_json()
    #except AttributeError:
    #    pass

    return obj


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
        config.validate_orjson()
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

        cleaned = promise_clean_to_json_compatible(cleaned)

        return orjson.dumps(cleaned, option=opts).decode("utf8")

import plotly.io.json
plotly.io.json.to_json_plotly = to_json_django_plotly
