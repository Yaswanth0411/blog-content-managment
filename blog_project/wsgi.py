"""
blog_project/wsgi.py

WSGI (Web Server Gateway Interface) config for blog_project.

This is the entry point for production web servers like Gunicorn or uWSGI.
It exposes the WSGI callable as a module-level variable named 'application'.
"""

import os
from django.core.wsgi import get_wsgi_application

# Tell Django which settings module to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

# This is the WSGI application object that the server calls
application = get_wsgi_application()
