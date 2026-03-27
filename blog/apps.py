"""
blog/apps.py

App configuration for the 'blog' app.
Django uses this to configure signal handlers and app metadata.
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'  # Must match the app folder name
    verbose_name = 'Blog CMS'  # Human-readable name shown in admin

    def ready(self):
        """
        Called when Django starts up.
        Import signals here so they get connected.
        Signals allow decoupled code — e.g., auto-create a profile when a user is created.
        """
        import blog.signals  # noqa: F401
