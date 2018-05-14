from django.db import models
from django.contrib import admin
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

from .dash_wrapper import get_stateless_by_name

import json

class DashApp(models.Model):
    '''
    An instance of this model represents a dash application and its internal state
    '''
    app_name = models.CharField(max_length=100, blank=False, null=False, unique=False)
    instance_name = models.CharField(max_length=100, unique=True, blank=True, null=False)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    base_state = models.TextField(null=False) # If mandating postgresql then this could be a JSONField
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instance_name

    def save(self, *args, **kwargs):
        if not self.instance_name:
            existing_count = DashApp.objects.filter(app_name=self.app_name).count()
            self.instance_name = "%s-%i" %(self.app_name, existing_count+1)
        if not self.slug or len(self.slug) < 2:
            self.slug = slugify(self.instance_name)
        super(DashApp, self).save(*args,**kwargs)

    def _stateless_dash_app(self):
        dd = getattr(self,'_stateless_dash_app_instance',None)
        if not dd:
            dd = get_stateless_by_name(self.app_name)
            setattr(self,'_stateless_dash_app_instance',dd)
        return dd

    def as_dash_instance(self):
        dd = self._stateless_dash_app()
        base = json.loads(self.base_state)
        return dd.form_dash_instance(replacements=base,
                                     specific_identifier=self.slug)

    def _get_base_state(self):
        '''
        Get the base state of the object, as defined by the app.layout code, as a python dict
        '''
        base_app_inst = self._stateless_dash_app()

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
    def locate_item(id, stateless=False):
        if stateless:
            da = get_stateless_by_name(id)
        else:
            da = get_object_or_404(DashApp,slug=id)

        app = da.as_dash_instance()
        return da, app

class DashAppAdmin(admin.ModelAdmin):
    list_display = ['instance_name','app_name','slug','creation','update',]
    list_filter = ['app_name','creation','update',]

    def _populate_values(self, request, queryset):
        for da in queryset:
            da.populate_values()
            da.save()
    _populate_values.short_description = "Populate app"

    actions = ['_populate_values',]
