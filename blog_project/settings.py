"""
Django settings for blog_project.

Full-featured Blog CMS with:
- User Authentication
- Rich Text Editor (CKEditor)
- Categories & Tags
- Comments System
"""

from pathlib import Path
import os

# ─────────────────────────────────────────────
# BASE DIRECTORY
# ─────────────────────────────────────────────
# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────
# IMPORTANT: Change this secret key in production and keep it secret!
SECRET_KEY = 'django-insecure-blogcms-secret-key-change-in-production-abc123xyz'

# IMPORTANT: Set DEBUG = False in production
DEBUG = True

# Add your domain here when deploying e.g. ['yourdomain.com']
ALLOWED_HOSTS = ['*']

# ─────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',        # Admin panel
    'django.contrib.auth',         # Authentication system
    'django.contrib.contenttypes', # Content types framework
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Flash messaging
    'django.contrib.staticfiles',  # Static file handling
    'django.contrib.humanize',     # Human-friendly data formatting

    # Third-party apps
    'ckeditor',                    # Rich text editor (WYSIWYG)
    'ckeditor_uploader',           # CKEditor file upload support
    'taggit',                      # Tags functionality

    # Our Blog app
    'blog',
]

# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',    # Handles sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',               # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentication
    'django.contrib.messages.middleware.MessageMiddleware',    # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─────────────────────────────────────────────
# URL & WSGI CONFIGURATION
# ─────────────────────────────────────────────
ROOT_URLCONF = 'blog_project.urls'
WSGI_APPLICATION = 'blog_project.wsgi.application'

# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global templates folder
        'APP_DIRS': True,                  # Look for templates inside each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
# Using SQLite for development. Switch to PostgreSQL for production.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Database file location
    }
}

# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Set to India timezone (IST)
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# STATIC FILES (CSS, JavaScript, Images)
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic puts files
STATICFILES_DIRS = [BASE_DIR / 'static']  # Extra static file locations

# ─────────────────────────────────────────────
# MEDIA FILES (User Uploaded Content)
# ─────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Where uploaded files are stored on disk

# ─────────────────────────────────────────────
# DEFAULT AUTO FIELD
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# AUTHENTICATION REDIRECTS
# ─────────────────────────────────────────────
LOGIN_URL = '/login/'           # Where to redirect if user is not logged in
LOGIN_REDIRECT_URL = '/'       # After successful login, go to homepage
LOGOUT_REDIRECT_URL = '/'      # After logout, go to homepage

# ─────────────────────────────────────────────
# CKEDITOR CONFIGURATION (Rich Text Editor)
# ─────────────────────────────────────────────
CKEDITOR_UPLOAD_PATH = 'uploads/'  # Where CKEditor uploads images (inside MEDIA_ROOT)

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            # Row 1: Document operations
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['Source'],  # HTML source view
        ],
        'height': 400,      # Editor height in pixels
        'width': '100%',    # Editor width (responsive)
        'extraPlugins': 'codesnippet',  # Code highlighting plugin
        'removePlugins': 'elementspath',
    },
}
