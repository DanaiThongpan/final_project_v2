"""
WSGI config for Website_recruiting_students_to_participate_in_activities project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Website_recruiting_students_to_participate_in_activities.settings')

application = get_wsgi_application()
