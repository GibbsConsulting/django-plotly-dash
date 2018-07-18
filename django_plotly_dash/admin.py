'Register models with the Django admin views'
from django.contrib import admin

from .models import (DashApp, DashAppAdmin,
                     StatelessApp, StatelessAppAdmin,
                    )

admin.site.register(DashApp, DashAppAdmin)
admin.site.register(StatelessApp, StatelessAppAdmin)
