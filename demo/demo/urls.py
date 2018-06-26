"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

from django.views.generic import TemplateView

# Load demo plotly apps
import demo.plotly_apps

urlpatterns = [
    url('^$', TemplateView.as_view(template_name='index.html'), name="home"),
    url('^second_page$', TemplateView.as_view(template_name='second_page.html'), name="second"),
    url('^admin/', admin.site.urls),
    url('^django_plotly_dash/', include('django_plotly_dash.urls')),
]

# Add in static routes so daphne can serve files; these should be masked eg with nginx for production use

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
