#!/usr/bin/env python

from setuptools import setup

import django_plotly_dash as dpd

VERSION = dpd.__version__

setup(
    name="django-plotly-dash",
    version=VERSION,
    description="Django use of plotly dash apps through template tags",
    author="Mark Gibbs",
    author_email="django_plotly_dash@gibbsconsulting.ca",
    packages=[
    'django_plotly_dash',
    ]
    )

