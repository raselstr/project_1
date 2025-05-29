import environ
import os
import dj_database_url
import socket


from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-8@p_g6dgio(5mmo)9zi*jqzkl2bc6*#6e#b7$#km@a$id1-6+i'
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# DEBUG = env('DEBUG')

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_htmx',
    'import_export',
    'django_tables2',
    'authapp',
    'dashboard',
    'opd',
    'dana',
    'dausg',
    'penerimaan',
    'rencana',
    'dankel',
    'pagu',
    'pendidikan',
    'kesehatan',
    'pu',
    'jadwal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'project.middleware.LoginRequiredMiddleware',
    'project.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project.context_processors.menu_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
try:
    socket.gethostbyname('db')
    print("INFO: Detected Docker environment, using DATABASE_URL")
    DEBUG = False
    DATABASES = {
        'default': dj_database_url.config(default=env('DATABASE_URL'))
    }
except (socket.gaierror, socket.error):
    print("INFO: Detected local environment, using DATABASE_URL_LOCAL")
    DEBUG = True
    DATABASES = {
        # 'default': dj_database_url.config(default=env('DATABASE_URL_LOCAL'))
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tkdd',
            'USER': 'raselstr',
            'PASSWORD': 'r283l8tr',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'id-id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

NUMBER_FORMAT = {
    'decimal_separator': ',',
    'thousand_separator': '.',
    'number_grouping': 3,
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Konversi Path menjadi string untuk STATIC_ROOT

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"  # Konversi Path menjadi string untuk MEDIA_ROOT

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
JQUERY_URL = True

LOGIN_URL = '/auth/login/'
# LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default, menggunakan database
SESSION_COOKIE_NAME = 'sessionid'  # Nama cookie session
SESSION_COOKIE_AGE = 1200  # Durasi sesi dalam detik 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Apakah session berakhir saat browser ditutup

# # Konfigurasi default (misalnya untuk pengembangan)
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

# # Jika lingkungan adalah produksi
# if os.getenv('DJANGO_ENV') == 'production':
#     LOGGING = {
#         'version': 1,
#         'disable_existing_loggers': False,
#         'handlers': {
#             'file': {
#                 'level': 'DEBUG',
#                 'class': 'logging.FileHandler',
#                 'filename': '/var/log/project_1/django.log',
#             },
#         },
#         'loggers': {
#             'django': {
#                 'handlers': ['file'],
#                 'level': 'DEBUG',
#                 'propagate': True,
#             },
#         },
#     }