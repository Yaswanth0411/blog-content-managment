"""
blog_project/urls.py

Main URL router for the entire Django project.
Every URL the user types in their browser is matched here first.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from blog import views as blog_views

urlpatterns = [
    # ─────────────────────────────────────────
    # ADMIN
    # ─────────────────────────────────────────
    # Django's built-in admin panel
    path('admin/', admin.site.urls),

    # ─────────────────────────────────────────
    # CKEDITOR (Rich Text Editor)
    # ─────────────────────────────────────────
    # Handles image uploads from within the editor
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # ─────────────────────────────────────────
    # AUTHENTICATION URLs
    # ─────────────────────────────────────────
    # Login page — uses Django's built-in LoginView with our custom template
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),

    # Logout — uses Django's built-in LogoutView
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Register — our custom view
    path('register/', blog_views.register, name='register'),

    # User profile page
    path('profile/', blog_views.profile, name='profile'),

    # ─────────────────────────────────────────
    # BLOG APP URLs
    # ─────────────────────────────────────────
    # All blog routes are handled inside blog/urls.py
    path('', include('blog.urls')),
]

# ─────────────────────────────────────────────
# MEDIA FILE SERVING (Development only)
# ─────────────────────────────────────────────
# In production, your web server (Nginx/Apache) serves media files.
# During development, Django serves them using this setting.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
