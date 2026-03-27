#!/usr/bin/env python
"""
manage.py

Django's command-line utility for administrative tasks.
This is the main entry point for running Django commands.

Common commands:
    python manage.py runserver         → Start development server
    python manage.py makemigrations    → Create migration files from model changes
    python manage.py migrate           → Apply migrations to the database
    python manage.py createsuperuser   → Create an admin account
    python manage.py collectstatic     → Gather static files for production
    python manage.py shell             → Open Django interactive Python shell
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Tell Django which settings file to use
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
