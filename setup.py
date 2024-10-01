#!/usr/bin/env python

from setuptools import setup


with open('django_plotly_dash/version.py') as f:
    exec(f.read())


with open('README.md') as f:
    long_description = f.read()


setup(
    name="django-plotly-dash",
    version=__version__,
    url="https://github.com/GibbsConsulting/django-plotly-dash",
    description="Django use of plotly dash apps through template tags",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mark Gibbs",
    author_email="django_plotly_dash@gibbsconsulting.ca",
    license='MIT',
    packages=[
    'django_plotly_dash',
    'django_plotly_dash.migrations',
    'django_plotly_dash.templatetags',
    ],
    include_package_data=True,
    classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Framework :: Dash',
    ],
    keywords='django plotly plotly-dash dash dashboard',
    project_urls = {
    'Source': "https://github.com/GibbsConsulting/django-plotly-dash",
    'Tracker': "https://github.com/GibbsConsulting/django-plotly-dash/issues",
    'Documentation': 'http://django-plotly-dash.readthedocs.io/',
    },
    install_requires = ['plotly',
                        'dash>=2.0,<3.0',
                        'dpd-components',

                        'dash-bootstrap-components',

                        'channels>=4.0',
                        'Django>=4.0.0',
                        'Flask>=1.0.2',
                        'Werkzeug',
    ],
    python_requires=">=3.8",
    )

