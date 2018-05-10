from django.db import models
from django.contrib import admin
from django.utils.text import slugify

from .dash_wrapper import get_app_instance_by_id, get_app_by_name, clear_app_instance

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
        # TODO at this point should invaliate any local cache of the older values
        clear_app_instance(self.slug)

    def as_dash_instance(self):
        ai = get_app_instance_by_id(self.slug)
        if ai:
            return ai
        dd = get_app_by_name(self.app_name)
        base = json.loads(self.base_state)
        return dd.form_dash_instance(replacements=base,
                                     specific_identifier=self.slug)

    @staticmethod
    def get_app_instance(id):
        '''
        Locate an application instance by id, either in local cache or in Database.
        If in neither, then create a new instance assuming that the id is the app name.
        '''
        local_instance = get_app_instance_by_id(id)
        if local_instance:
            return local_instance
        try:
            return DashApp.objects.get(slug=id).as_dash_instance()
        except:
            pass

        # Really no luck at all!
        dd = get_app_by_name(id)
        return dd.form_dash_instance()

class DashAppAdmin(admin.ModelAdmin):
    list_display = ['app_name','instance_name','slug','creation','update',]
    list_filter = ['app_name','creation','update',]

