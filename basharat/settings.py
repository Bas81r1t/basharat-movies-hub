import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import cloudinary
import dj_database_url

# ✅ Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Load .env (local development)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# ✅ Secret Key & Debug - CRITICAL: Added .strip()
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key').strip()
# IMPORTANT: Render par DEBUG ko False rakho for production
DEBUG = config('DEBUG', default=False, cast=bool) 

ALLOWED_HOSTS = [
    'basharat-movies-hub.onrender.com',
    'localhost',
    '127.0.0.1',
    'testserver' 
]

# (INSTALLED_APPS, MIDDLEWARE, ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION sections are unchanged)
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'basharat.urls'

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

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL").strip(), # Added .strip()
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ✅ Cloudinary Configuration - Added .strip() everywhere
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

# ✅ Email Configuration - CRITICAL FIX: Added .strip()
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend').strip()
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com').strip()
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30 

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='bas81r1t@gmail.com').strip()
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='dxagtxtqfesjcyof').strip()
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER).strip()

# ✅ Auto Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
