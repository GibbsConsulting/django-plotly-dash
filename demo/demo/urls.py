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

# pylint: disable=wrong-import-position,wrong-import-order

from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

# Load demo plotly apps - this triggers their registration
import demo.plotly_apps    # pylint: disable=unused-import
import demo.dash_apps      # pylint: disable=unused-import
import demo.bootstrap_app  # pylint: disable=unused-import

from django_plotly_dash.views import add_to_session

from .views import dash_example_1_view, session_state_view

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name="home"),
    path('demo-one', TemplateView.as_view(template_name='demo_one.html'), name="demo-one"),
    path('demo-two', TemplateView.as_view(template_name='demo_two.html'), name="demo-two"),
    path('demo-three', TemplateView.as_view(template_name='demo_three.html'), name="demo-three"),
    path('demo-four', TemplateView.as_view(template_name='demo_four.html'), name="demo-four"),
    path('demo-five', TemplateView.as_view(template_name='demo_five.html'), name="demo-five"),
    path('demo-six', dash_example_1_view, name="demo-six"),
    path('demo-seven', TemplateView.as_view(template_name='demo_seven.html'), name="demo-seven"),
    path('demo-eight', session_state_view, {'template_name':'demo_eight.html'}, name="demo-eight"),
    path('demo-nine', TemplateView.as_view(template_name='demo_nine.html'), name="demo-nine"),
    path('demo-ten', TemplateView.as_view(template_name='demo_ten.html'), name="demo-ten"),
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

    path('demo-session-var', add_to_session, name="session-variable-example"),
]

# Add in static routes so daphne can serve files; these should
# be masked eg with nginx for production use

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
