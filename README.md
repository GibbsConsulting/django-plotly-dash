# django-plotly-dash

[![PyPI version](https://badge.fury.io/py/django-plotly-dash.svg)](https://badge.fury.io/py/django-plotly-dash)
![Develop Branch Build Status](https://travis-ci.org/GibbsConsulting/django-plotly-dash.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/GibbsConsulting/django-plotly-dash/badge.svg?branch=master)](https://coveralls.io/github/GibbsConsulting/django-plotly-dash?branch=master)
[!Downloads](https://img.shields.io/pypi/dw/:package.svg)

Expose [plotly dash](https://plot.ly/products/dash/) apps as [Django](https://www.djangoproject.com/) tags. Multiple Dash apps can
then be embedded into a single web page, persist and share internal state, and also have access to the
current user and session variables.

See the source for this project here:
<https://github.com/GibbsConsulting/django-plotly-dash>

This README file provides a short guide to installing and using the package, and also
outlines how to run the demonstration application.

More detailed information
can be found in the online documentation at
<https://readthedocs.org/projects/django-plotly-dash>


## Installation

First, install the package. This will also install plotly and some dash packages if they are not already present.

    pip install django_plotly_dash

Then, just add `django_plotly_dash` to `INSTALLED_APPS` in your Django `settings.py` file

    INSTALLED_APPS = [
        ...
        'django_plotly_dash.apps.DjangoPlotlyDashConfig',
        ...
        ]

Note that this package requires version 2.0 or greater of Django, due to the use of the `path` function for registering routes.

Live updating of applications, to share application
state, requires further
configuration. See the [online documentation](https://django-plotly-dash.readthedocs.io/en/latest/) for more details.

## Demonstration

The source repository contains a demo application. To clone the repo and lauch the demo:

```bash
git clone https://github.com/GibbsConsulting/django-plotly-dash.git

cd django-plotly-dash

./make_env                # sets up a virtual environment for development
                          #   with direct use of the source code for the package

./prepare_redis           # downloads a redis docker container
                          #   and launches it with default settings
                          #   *THIS STEP IS OPTIONAL*

./prepare_demo            # prepares and launches the demo
                          #   using the Django debug server at http://localhost:8000
```

## Usage

To use existing dash applications, first register them using the `DjangoDash` class. This
replaces the `Dash` class of the `dash` package.

Taking a very simple example inspired by the excellent [getting started](https://dash.plot.ly/) documentation:

```python
import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash

app = DjangoDash('SimpleExample')

app.layout = html.Div([
    dcc.RadioItems(
        id='dropdown-color',
        options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
        value='red'
    ),
    html.Div(id='output-color'),
    dcc.RadioItems(
        id='dropdown-size',
        options=[{'label': i, 'value': j} for i, j in [('L','large'), ('M','medium'), ('S','small')]],
        value='medium'
    ),
    html.Div(id='output-size')

])

@app.callback(
    dash.dependencies.Output('output-color', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value')])
def callback_color(dropdown_value):
    return "The selected color is %s." % dropdown_value

@app.callback(
    dash.dependencies.Output('output-size', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value'),
     dash.dependencies.Input('dropdown-size', 'value')])
def callback_size(dropdown_color, dropdown_size):
    return "The chosen T-shirt is a %s %s one." %(dropdown_size,
                                                  dropdown_color)
```

Note that the `DjangoDash` constructor requires a name to be specified. This name is then used to identify the dash app in
templates:

```jinja2
{% load plotly_dash %}

{% plotly_app name="SimpleExample" %}
```

The registration code needs to be in a location
that will be imported into the Django process before any model or template tag attempts to use it. The example Django application
in the demo subdirectory achieves this through an import in the main `urls.py` file; any `views.py` would also be sufficient.

Whilst this example allows for the direct use of existing `Dash` applications, it does not provide for the sharing or updating of
internal state. The [online documentation](https://django-plotly-dash.readthedocs.io/en/latest/) provides details on using these
and other additional features.

## Development

The `make_env` script sets up the development environment, and pulls in the packages
specified in the `dev_requirements.txt` file. The `check_code` script invokes the test suite (using `pytest`) as well
as invoking `pylint` on both the package and the associated demo.
