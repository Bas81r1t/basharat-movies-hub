import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import cloudinary
import dj_database_url

# ------------------------------
# ✅ Base Directory
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# ✅ Load .env file
# ------------------------------
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# ------------------------------
# ✅ Secret Key & Debug Mode
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
# ✅ Installed Apps
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
# ✅ Middleware
# ------------------------------
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

# ------------------------------
# ✅ Templates
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
# ✅ Database Configuration
# ------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL").strip(),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ------------------------------
# ✅ Password Validators
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------
# ✅ Language & Timezone
# ------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ------------------------------
# ✅ Static Files
# ------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ------------------------------
# ✅ Media Files
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------
# ✅ Cloudinary Configuration
# ------------------------------
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUD_NAME', default='').strip(),
    'API_KEY': config('API_KEY', default='').strip(),
    'API_SECRET': config('API_SECRET', default='').strip(),
}
cloudinary.config(
    cloud_name=config('CLOUD_NAME', default='').strip(),
    api_key=config('API_KEY', default='').strip(),
    api_secret=config('API_SECRET', default='').strip(),
    secure=True
)

# ------------------------------
# ✅ Email Configuration (from os.getenv)
# ------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_TIMEOUT = 60

# ------------------------------
# ✅ CSRF Trusted Origins
# ------------------------------
CSRF_TRUSTED_ORIGINS = [
    'https://basharat-movies-hub.onrender.com'
]

# ------------------------------
# ✅ Auto Field
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
