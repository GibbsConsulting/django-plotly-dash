# dpd with html return

This is a simple extension of the django-plotly-dash v0.6.0 package to include an option to return html instead of an iframe to a django view.
Included is the amended package code as well as a demo.

to get up and running, clone this repo then start a new env running the following:

`pip install -r requirements.txt`   - note that specific versions of Dash are used in this for this demo

`pip install -r dev_requirements.txt`

`python setup.py install` in the root folder to install this dpd extension


Now run the dpd_html_return_demo, which should just run as is using python manage.py runserver. Navigate to http://127.0.0.1:8000/django_app/dash_example_1 to view a simple dashboard.
