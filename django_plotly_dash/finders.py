'''
Staticfiles finders for Dash assets

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

import os
import importlib

from collections import OrderedDict

from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.utils import get_files

from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django.apps import apps

from django_plotly_dash.dash_wrapper import all_apps
from django_plotly_dash.util import full_asset_path

class DashComponentFinder(BaseFinder):
    'Find static files in components'

    #pylint: disable=abstract-method, redefined-builtin

    def __init__(self):

        self.locations = []
        self.storages = OrderedDict()
        self.components = {}

        self.ignore_patterns = ["*.py", "*.pyc",]

        try:
            components = settings.PLOTLY_COMPONENTS
        except:
            components = []

        for component_name in components:

            module = importlib.import_module(component_name)
            path_directory = os.path.dirname(module.__file__)

            root = path_directory
            storage = FileSystemStorage(location=root)
            path = "dash/component/%s" % component_name

            # Path_directory is where from
            # path is desired url mount point of the content of path_directory
            # component_name is the name of the component

            storage.prefix = path

            self.locations.append(component_name)

            self.storages[component_name] = storage
            self.components[path] = component_name

        super().__init__()

    def find(self, path, all=False):
        matches = []
        for component_name in self.locations:
            storage = self.storages[component_name]
            location = storage.location # dir on disc

            component_path = "dash/component/%s" % component_name
            if len(path) > len(component_path) and path[:len(component_path)] == component_path:

                matched_path = os.path.join(location, path[len(component_path)+1:])
                if os.path.exists(matched_path):
                    if not all:
                        return matched_path
                    matches.append(matched_path)

        return matches

    # pylint: disable=inconsistent-return-statements, no-self-use
    def find_location(self, path):
        'Return location, if it exists'
        if os.path.exists(path):
            return path

    def list(self, ignore_patterns):
        for component_name in self.locations:
            storage = self.storages[component_name]
            for path in get_files(storage, ignore_patterns + self.ignore_patterns):
                yield path, storage

class DashAppDirectoryFinder(BaseFinder):
    'Find static fies in application subdirectories'

    def __init__(self):
        # get all registered apps

        self.locations = []
        self.storages = OrderedDict()

        self.ignore_patterns = ["*.py", "*.pyc",]

        for app_config in apps.get_app_configs():

            path_directory = os.path.join(app_config.path, 'assets')

            if os.path.isdir(path_directory):

                storage = FileSystemStorage(location=path_directory)

                storage.prefix = full_asset_path(app_config.name, "")

                self.locations.append(app_config.name)
                self.storages[app_config.name] = storage

        super().__init__()

    #pylint: disable=redefined-builtin
    def find(self, path, all=False):
        return []

    def list(self, ignore_patterns):
        for component_name in self.locations:
            storage = self.storages[component_name]
            for path in get_files(storage, ignore_patterns + self.ignore_patterns):
                yield path, storage


class DashAssetFinder(BaseFinder):
    'Find static files in asset directories'

    #pylint: disable=unused-import, unused-variable, no-name-in-module, import-error, abstract-method

    def __init__(self):

        # Ensure urls are loaded
        root_urls = settings.ROOT_URLCONF
        importlib.import_module(root_urls)

        # Get all registered django dash apps

        self.apps = all_apps()

        self.locations = []
        self.storages = OrderedDict()

        self.ignore_patterns = ["*.py", "*.pyc",]

        added_locations = {}

        for app_slug, obj in self.apps.items():

            caller_module = obj.caller_module
            location = obj.caller_module_location
            subdir = obj.assets_folder

            path_directory = os.path.join(os.path.dirname(location), subdir)

            if os.path.isdir(path_directory):

                component_name = app_slug
                storage = FileSystemStorage(location=path_directory)
                path = full_asset_path(obj.caller_module.__name__,"")
                storage.prefix = path

                self.locations.append(component_name)
                self.storages[component_name] = storage

        super().__init__()

    #pylint: disable=redefined-builtin
    def find(self, path, all=False):
        return []

    def list(self, ignore_patterns):
        for component_name in self.locations:
            storage = self.storages[component_name]
            for path in get_files(storage, ignore_patterns + self.ignore_patterns):
                yield path, storage

