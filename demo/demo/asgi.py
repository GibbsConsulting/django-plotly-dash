'Configure asgi server for serving asynchronous content such as websockets'

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")

django.setup()

application = get_default_application()
