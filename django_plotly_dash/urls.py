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

from .views import routes, layout, dependencies, update, main_view, component_suites, component_component_suites, asset_redirection
from .views import add_stateless_apps

from .app_name import app_name, main_view_label

from .access import process_view_function

urlpatterns = [
    path('add_stateless_apps',add_stateless_apps,name='add_stateless_apps'),
    ]

for base_type, args, name_prefix, url_ending, name_suffix in [('instance', {}, '', '', '', ),
                                                              ('app', {'stateless':True}, 'app-', '', '', ),
                                                              ('instance', {}, '', '/initial/<slug:cache_id>', '--args', ),
                                                              ('app', {'stateless':True}, 'app-', '/initial/<slug:cache_id>', '--args', ),
                                                             ]:

    for url_part, view_function, name, url_suffix in [('_dash-routes', routes, 'routes', '', ),
                                                      ('_dash-layout', layout, 'layout', '', ),
                                                      ('_dash-dependencies', dependencies, 'dependencies', '', ),
                                                      ('_dash-update-component', csrf_exempt(update), 'update-component', '', ),
                                                      ('', main_view, main_view_label, '', ),
                                                      ('_dash-component-suites', component_suites, 'component-suites', '/<slug:component>/<resource>', ),
                                                      ('_dash-component-suites', component_component_suites, 'component-component-suites', '/<slug:component>/_components/<resource>', ),
                                                      ('assets', asset_redirection, 'asset-redirect', '/<path:path>', ),
                                                     ]:

        route_name = '%s%s%s' % (name_prefix, name, name_suffix)
        wrapped_view_function = process_view_function(view_function,
                                                      route_name=route_name,
                                                      url_part=url_part,
                                                      name=name)
        urlpatterns.append(path('%s/<slug:ident>%s/%s%s' % (base_type, url_ending, url_part, url_suffix),
                                wrapped_view_function,
                                args,
                                name=route_name))
