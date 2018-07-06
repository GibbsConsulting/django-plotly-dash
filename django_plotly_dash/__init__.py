'''
Django-plotly-dash
==================

This module provides a wrapper around a Plotly Dash instance
and enables it to be served as part of a Django application.
'''

__version__ = "0.4.3"

from .dash_wrapper import DjangoDash
from .consumers import send_to_pipe_channel
