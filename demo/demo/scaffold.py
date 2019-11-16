'Test harness code'

from django_plotly_dash import DjangoDash
from django.utils.module_loading import import_string

from demo.plotly_apps import multiple_callbacks

def stateless_app_loader(app_name):

    # Load a stateless app
    return import_string("demo.scaffold." + app_name)

demo_app = DjangoDash(name="name_of_demo_app")

