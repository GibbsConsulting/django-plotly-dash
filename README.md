# django-plotly-dash

Expose [plotly dash](https://plot.ly/products/dash/) apps as django tags.

See the source for this project here:
<https://github.com/GibbsConsulting/django-plotly-dash>

Online documentation can be found here:
<https://readthedocs.org/projects/django-plotly-dash>

## Installation

First, install the package. This will also install plotly and some dash packages if they are not already present.

    pip install django_plotly_dash

Then, just add `django_plotly_dash` to `INSTALLED_APPS` in your Django `settings.py` file

    INSTALLED_APPS = [
        ...
        'django_plotly_dash',
        ...
        ]

## Demonstration

The source repository contains a demo application. To clone the repo and lauch the demo:

```bash
git clone https://github.com/GibbsConsulting/django-plotly-dash.git

cd django-plotly-dash

./make_env                # sets up a virtual environment for development
                          #   with direct use of the source code for the package

./prepare_demo            # prepares and launches the demo
                          #   using the Django debug server at http://localhost:8000
```

## Usage

To use existing dash applications, first register them using the `DelayedDash` class. This
replaces the `dash.Dash` class of `plotly.py.`

Taking as an example a slightly modified variant of one of the [getting started](https://dash.plot.ly/getting-started-part-2) examples:

```python
import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DelayedDash

app = DelayedDash('SimpleExample')   # replaces dash.Dash

app.layout = html.Div([
    dcc.RadioItems(
        id='dropdown-a',
        options=[{'label': i, 'value': i} for i in ['Canada', 'USA', 'Mexico']],
        value='Canada'
    ),
    html.Div(id='output-a'),

    dcc.RadioItems(
        id='dropdown-b',
        options=[{'label': i, 'value': i} for i in ['MTL', 'NYC', 'SF']],
        value='MTL'
    ),
    html.Div(id='output-b')

])

@app.callback(
    dash.dependencies.Output('output-a', 'children'),
    [dash.dependencies.Input('dropdown-a', 'value')])
def callback_a(dropdown_value):
    return 'You\'ve selected "{}"'.format(dropdown_value)


@app.callback(
    dash.dependencies.Output('output-b', 'children'),
    [dash.dependencies.Input('dropdown-a', 'value'),
     dash.dependencies.Input('dropdown-b', 'value')])
def callback_b(dropdown_value,other_dd):
    return 'You\'ve selected "{}" and "{}"'.format(dropdown_value,
                                                   other_dd)
```

Note that the `DelayedDash` constructor requires a name to be specified. This name is then used to identify the dash app in
templates:

```jinja2
{% load plotly_dash %}

{% plotly_item "SimpleExample" %}
```

Note that the registration code needs to be in a location
that will be imported into the Django process before any template tag attempts to use it. The example Django application
in the demo subdirectory achieves this through an import in the main urls.py file; any views.py would also be sufficient.

