from django.contrib import admin

from .models import DashApp, DashAppAdmin

admin.site.register(DashApp, DashAppAdmin)

