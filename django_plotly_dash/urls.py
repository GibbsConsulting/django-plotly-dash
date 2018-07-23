'''
url routes for serving dash applications

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

# pylint: disable = unused-import

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import routes, layout, dependencies, update, main_view, component_suites

from .app_name import app_name, main_view_label

urlpatterns = [
    path('instance/<slug:ident>_dash-routes', routes, name="routes"),
    path('instance/<slug:ident>_dash-layout', layout, name="layout"),
    path('instance/<slug:ident>_dash-dependencies', dependencies, name="dependencies"),
    path('instance/<slug:ident>_dash-update-component',
         csrf_exempt(update), name="update-component"),
    path('instance/<slug:ident>', main_view, name=main_view_label),
    path('instance/<slug:ident>_dash-component-suites/<slug:component>/<resource>',
         component_suites, name='component-suites'),

    path('app/<slug:ident>_dash-routes', routes, {'stateless':True}, name="app-routes"),
    path('app/<slug:ident>_dash-layout', layout, {'stateless':True}, name="app-layout"),
    path('app/<slug:ident>_dash-dependencies',
         dependencies, {'stateless':True}, name="app-dependencies"),
    path('app/<slug:ident>_dash-update-component',
         csrf_exempt(update), {'stateless':True}, name="app-update-component"),
    path('app/<slug:ident>', main_view, {'stateless':True}, name='app-%s'%main_view_label),
    path('app/<slug:ident>_dash-component-suites/<slug:component>/<resource>',
         component_suites, {'stateless':True}, name='app-component-suites'),
    ]
