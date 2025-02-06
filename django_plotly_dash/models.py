'''
Django ORM models for dash applications

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

import json
import logging

from django.db import models
from django.contrib import admin
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

from .dash_wrapper import get_local_stateless_by_name, get_local_stateless_list, wid2str, DjangoDash

logger = logging.getLogger(__name__)


def get_stateless_by_name(name):
    'Locate stateless app instance given its name'
    return get_local_stateless_by_name(name)


class StatelessApp(models.Model):
    '''
    A stateless Dash app. An instance of this model represents a dash app without any specific state
    '''
    app_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    def __str__(self):
        return self.app_name

    def save(self, *args, **kwargs): # pylint: disable=arguments-differ
        if not self.slug or len(self.slug) < 2:
            self.slug = slugify(self.app_name)
            exist_count = StatelessApp.objects.filter(slug__startswith=self.slug).count()
            if exist_count > 0:
                self.slug = self.slug + str(exist_count+1)
        return super().save(*args, **kwargs)

    def as_dash_app(self) -> DjangoDash:
        '''
        Return a DjangoDash instance of the dash application
        '''
        dateless_dash_app = getattr(self, '_stateless_dash_app_instance', None)
        if not dateless_dash_app:
            dateless_dash_app = get_stateless_by_name(self.app_name)
            setattr(self, '_stateless_dash_app_instance', dateless_dash_app)
        return dateless_dash_app

def find_stateless_by_name(name):
    '''
    Find stateless app given its name

    First search the Django ORM, and if not found then look the app up in a local registry.
    If the app does not have an ORM entry then a StatelessApp model instance is created.
    '''
    try:
        dsa_app = StatelessApp.objects.get(app_name=name) # pylint: disable=no-member
        return dsa_app.as_dash_app()
    except: # pylint: disable=bare-except
        pass

    dash_app = get_stateless_by_name(name)
    dsa_app = StatelessApp(app_name=name)
    dsa_app.save()
    return dash_app


def check_stateless_loaded():
    for ua in get_local_stateless_list():
        try:
            find_stateless_by_name(ua)
        except:
            logger.warning("django-plotly-dash: Unable to create stateless instance: "+str(ua))


class StatelessAppAdmin(admin.ModelAdmin):
    'Admin for StatelessApp ORM model instances'
    list_display = ['app_name', 'slug',]
    list_filter = ['app_name', 'slug',]

    def check_registered(modeladmin, request, queryset):
        # Check all existing apps, keep if OK
        for sa in queryset.all():
            try:
                q = sa.as_dash_app()
            except:
                logger.warning("django-plotly-dash: Unable to load stateless app: "+str(sa))


    check_registered.short_description = "Check stateless apps"

    actions = [check_registered,]


class DashApp(models.Model):
    '''
    An instance of this model represents a dash application and its internal state
    '''
    stateless_app = models.ForeignKey(StatelessApp, on_delete=models.PROTECT,
                                      unique=False, null=False, blank=False)
    instance_name = models.CharField(max_length=100, unique=True,
                                     blank=True, null=False)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    # If mandating postgresql then this could be a JSONField
    base_state = models.TextField(null=False, default="{}")

    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    save_on_change = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.instance_name

    def save(self, *args, **kwargs): # pylint: disable=arguments-differ
        if not self.instance_name:
            existing_count = DashApp.objects.all().count() # pylint: disable=no-member
            self.instance_name = "%s-%i" %(self.stateless_app.app_name, existing_count+1) # pylint: disable=no-member
        if not self.slug or len(self.slug) < 2:
            self.slug = slugify(self.instance_name)
        super().save(*args, **kwargs)

    def handle_current_state(self):
        '''
        Check to see if the current hydrated state and the saved state are different.

        If they are, then persist the current state in the database by saving the model instance.
        '''
        if getattr(self, '_current_state_hydrated_changed', False) and self.save_on_change:
            new_base_state = json.dumps(getattr(self, '_current_state_hydrated', {}))
            if new_base_state != self.base_state:
                self.base_state = new_base_state
                self.save()

    def have_current_state_entry(self, wid, key):
        'Return True if there is a cached current state for this app'
        cscoll = self.current_state()
        c_state = cscoll.get(wid2str(wid), {})
        return key in c_state

    def update_current_state(self, wid, key, value):
        '''
        Update current state with a (possibly new) value associated with key

        If the key does not represent an existing entry, then ignore it
        '''
        cscoll = self.current_state()
        c_state = cscoll.get(wid2str(wid), {})
        if key in c_state:
            current_value = c_state.get(key, None)
            if current_value != value:
                c_state[key] = value
                setattr(self, '_current_state_hydrated_changed', True)

    def current_state(self):
        '''
        Return the current internal state of the model instance.

        This is not necessarily the same as the persisted state
        stored in the self.base_state variable.
        '''
        c_state = getattr(self, '_current_state_hydrated', None)
        if not c_state:
            c_state = json.loads(self.base_state)
            setattr(self, '_current_state_hydrated', c_state)
            setattr(self, '_current_state_hydrated_changed', False)
        return c_state

    def as_dash_instance(self, cache_id=None):
        'Return a dash application instance for this model instance'
        dash_app = self.stateless_app.as_dash_app() # pylint: disable=no-member
        base = self.current_state()
        return dash_app.do_form_dash_instance(replacements=base,
                                              specific_identifier=self.slug,
                                              cache_id=cache_id)

    def _get_base_state(self):
        '''
        Get the base state of the object, as defined by the app.layout code, as a python dict
        '''
        base_app_inst = self.stateless_app.as_dash_app().as_dash_instance() # pylint: disable=no-member

        # Get base layout response, from a base object
        base_resp = base_app_inst.locate_endpoint_function('dash-layout')()

        base_obj = json.loads(base_resp.data.decode('utf-8'))

        # Walk the base layout and find all values; insert into base state map
        obj = {}
        base_app_inst.walk_tree_and_extract(base_obj, obj)
        return obj

    def populate_values(self):
        '''
        Add values from the underlying dash layout configuration
        '''
        obj = self._get_base_state()
        self.base_state = json.dumps(obj)

    @staticmethod
    def locate_item(ident, stateless=False, cache_id=None):
        '''Locate a dash application, given either the
        slug of an instance or the name for a stateless app'''
        if stateless:
            dash_app = find_stateless_by_name(ident)
        else:
            dash_app = get_object_or_404(DashApp, slug=ident)

        app = dash_app.as_dash_instance(cache_id=cache_id)
        return dash_app, app

class DashAppAdmin(admin.ModelAdmin):
    'Admin class for DashApp model'
    list_display = ['instance_name', 'stateless_app', 'slug',
                    'creation', 'update', 'save_on_change',]
    list_filter = ['creation', 'update', 'save_on_change', 'stateless_app',]

    def _populate_values(self, request, queryset): # pylint: disable=no-self-use, unused-argument
        for dash_app in queryset:
            dash_app.populate_values()
            dash_app.save()
    _populate_values.short_description = "Populate app instance"

    def _clone(self, request, queryset): # pylint: disable=no-self-use, unused-argument
        for dash_app in queryset:
            nda = DashApp(stateless_app=dash_app.stateless_app,
                          base_state=dash_app.base_state,
                          save_on_change=dash_app.save_on_change)
            nda.save()

    _clone.short_description = "Clone app instance"

    actions = ['_populate_values', '_clone',]
