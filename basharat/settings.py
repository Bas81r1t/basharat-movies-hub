import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import cloudinary
import dj_database_url

# ------------------------------
# Base Directory
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# Load .env file (for local development)
# ------------------------------
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# ------------------------------
# Secret Key & Debug Mode
# ------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key').strip()
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'basharat-movies-hub.onrender.com',
    'localhost',
    '127.0.0.1',
    'testserver'
]

# ------------------------------
# Installed Apps
# ------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom app
    'movies.apps.MoviesConfig',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # SEO
    'django.contrib.sitemaps',
]

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise is essential for serving static files on Render
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'basharat.urls'

# ------------------------------
# Templates
# ------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'basharat.wsgi.application'

# ------------------------------
# Database Configuration
# ------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL").strip(),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ------------------------------
# Password Validators
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------
# Language & Timezone
# ------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static Files
# ------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ------------------------------
# Media Files (Handled by Cloudinary)
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------
# Cloudinary Configuration
# ------------------------------
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUD_NAME').strip(),
    'API_KEY': config('API_KEY').strip(),
    'API_SECRET': config('API_SECRET').strip(),
}
cloudinary.config(
    cloud_name=config('CLOUD_NAME').strip(),
    api_key=config('API_KEY').strip(),
    api_secret=config('API_SECRET').strip(),
    secure=True
)

# ------------------------------
# Email Configuration (Production Ready)
# ------------------------------
# Note: config() uses environment variables on Render
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend').strip()
EMAIL_HOST = config('EMAIL_HOST').strip()
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)

# Sendinblue (Brevo) typically uses TLS on port 587.
# Use 'default=False' for booleans to avoid issues if not set in environment.
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=False)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool, default=False) 

EMAIL_HOST_USER = config('EMAIL_HOST_USER').strip()
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD').strip() 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL').strip()

# Increase timeout to prevent Render worker timeouts during send
EMAIL_TIMEOUT = 60

# -------------------------------------------------------------
# Custom Notification Configuration (For Movie Requests)
# -------------------------------------------------------------
# Define the email addresses that will receive the movie request notifications.
ADMIN_NOTIFY_EMAILS_RAW = config('ADMIN_NOTIFY_EMAILS', default='').strip()
ADMIN_NOTIFY_EMAIL = [email.strip() for email in ADMIN_NOTIFY_EMAILS_RAW.split(',') if email.strip()]

# Agar koi specific email nahi set kiya gaya hai, toh default bhejnewale email ko use karo.
if not ADMIN_NOTIFY_EMAIL and EMAIL_HOST_USER:
    ADMIN_NOTIFY_EMAIL = [EMAIL_HOST_USER]


# ------------------------------
# CSRF Trusted Origins
# ------------------------------
CSRF_TRUSTED_ORIGINS = [
    'https://basharat-movies-hub.onrender.com'
]

# ------------------------------
# Auto Field
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
