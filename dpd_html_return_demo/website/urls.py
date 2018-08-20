from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [

    #admin
    path('admin/', admin.site.urls),

    # app:
    path('django_app/', include('django_app.urls')),
    url('^django_plotly_dash/', include('django_plotly_dash.urls')),

    ]

if settings.DEBUG == True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
