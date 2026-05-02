import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if os.name == 'nt':
    os.environ['PATH'] = r'C:\OSGeo4W\bin;' + os.environ.get('PATH', '')
    GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal312.dll'
    GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'

SECRET_KEY = 'django-insecure-gis-qldd-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.gis',
    'rest_framework',
    'channels',
    'myapp',
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

ROOT_URLCONF = 'QLDD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'myapp' / 'templates'],
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

WSGI_APPLICATION = 'QLDD.wsgi.application'
ASGI_APPLICATION = 'QLDD.asgi.application'

# --- Channels Layer (In-Memory for Dev) ---
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# --- Cơ sở dữ liệu PostgreSQL ---
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'qldd_db',
        'USER': 'postgres',
        'PASSWORD': 'Nghia23042005az',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# --- Ngôn ngữ và múi giờ Việt Nam ---
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'myapp' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Authentication ---
LOGIN_URL = 'dang_nhap'
LOGIN_REDIRECT_URL = 'tong_quan'
LOGOUT_REDIRECT_URL = 'dang_nhap'

# --- OpenRouteService API Key ---
# Đăng ký miễn phí tại: https://openrouteservice.org/dev/
ORS_API_KEY = '5b3ce3597851110001cf6248fd2a9ff7c8864417a0ef3f6ea0d6ab28'
