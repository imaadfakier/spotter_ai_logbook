"""
WSGI config for spotter_ai_trucker_logbook project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the outer directory to sys.path so the app can find modules in the nested folder
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotter_ai_trucker_logbook.settings")

application = get_wsgi_application()
