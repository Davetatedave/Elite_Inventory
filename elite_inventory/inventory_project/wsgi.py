"""
WSGI config for tracker_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

env = os.getenv("GAE_VERSION", "local")

if env != "local":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "inventory_project.settings.cloud_settings"
    )
else:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "inventory_project.settings.settings"
    )

application = get_wsgi_application()
