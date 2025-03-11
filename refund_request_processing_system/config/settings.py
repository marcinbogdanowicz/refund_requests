import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from import_export.formats.base_formats import CSV

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'insecure-secret-key',
)

DEBUG = int(os.getenv('DEBUG', 1))

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'import_export',
    'apps.core',
    'apps.refunds',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.UserRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'user': '100/day'},
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "DATABASE_ENGINE", "django.db.backends.sqlite3"
        ),
        "USER": os.environ.get("DATABASE_USER", "user"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", "password"),
        "HOST": os.environ.get("DATABASE_HOST", "localhost"),
        "PORT": os.environ.get("DATABASE_PORT", "5432"),
        "NAME": os.environ.get("DATABASE_DB", "sqlite3.db"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))

DEFAULT_FROM_EMAIL = 'no-reply@example.com'

LOGIN_REDIRECT_URL = reverse_lazy('refund_list')

API_NINJAS_API_KEY = os.getenv(
    'API_NINJAS_API_KEY', '4r5s/X/fxaljNyCcrlldlA==jK1lAnTXcbRTDUQS'
)
API_NINJAS_IBAN_VALIDATION_URL = 'https://api.api-ninjas.com/v1/iban'


CACHE_BACKEND = os.getenv(
    'CACHE_BACKEND', 'django.core.cache.backends.filebased.FileBasedCache'
)
if CACHE_BACKEND == 'django.core.cache.backends.redis.RedisCache':
    REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME', 'redis')
    REDIS_MAIN_DB = os.getenv('REDIS_MAIN_DB', 0)
    REDIS_CACHE_VERSION = 1
    CACHES = {
        'default': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': f'redis://{REDIS_HOSTNAME}/{REDIS_MAIN_DB}',
            'VERSION': REDIS_CACHE_VERSION,
            'TIMEOUT': 3600,  # 1 hour
        }
    }
elif CACHE_BACKEND == 'django.core.cache.backends.filebased.FileBasedCache':
    CACHES = {
        'default': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': BASE_DIR / 'cache',
        }
    }
else:
    raise ImproperlyConfigured(
        f'Configure cache backend {CACHE_BACKEND} before using it.'
    )

IMPORT_EXPORT_FORMATS = [CSV]
