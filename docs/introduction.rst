.. _introduction:

Introduction
============

The purpose of django-plotly-dash is to enable Plotly Dash applications to be served up as part of a Django application, in order to provide
these features:

* Multiple dash applications can be used on a single page
* Separate instances of a dash application can persist along with internal state
* Leverage user management and access control and other parts of the Django infrastructure
* Consolidate into a single server process to simplify scaling

There is nothing here that cannot be achieved through expanding the Flask app around Plotly Dash, or indeed by using an alternative web
framework. The purpose of this project is to enable the above features, given that the choice to use Django has already been made.
