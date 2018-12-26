'''
Control url access based on user and other state

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

import importlib
from django.conf import settings

from django.contrib.auth.decorators import login_required as login_required_decorator

#pylint: disable=bare-except, unused-argument

def login_required(view_function, **kwargs):
    'Wrap all DPD calls with login_required'
    return login_required_decorator(view_function)

try:
    dash_view_decorator_name = settings.PLOTLY_DASH['view_decorator']
    try:
        dash_view_decorator = locals()[dash_view_decorator_name]
    except:
        mod_name, func_name = dash_view_decorator_name.rsplit('.', 1)
        if mod_name:
            mod = importlib.import_module(mod_name)
            dash_view_decorator = getattr(mod, func_name)
        else:
            dash_view_decorator = locals()[func_name]
except:
    dash_view_decorator = None

def process_view_function(view_function, **kwargs):
    'Process view function and wrap according to settings'

    if dash_view_decorator:
        return dash_view_decorator(view_function, **kwargs)

    return view_function
