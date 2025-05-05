from decouple import Config, RepositoryEnv
from os import path, curdir

file_path = path.dirname(path.abspath(__file__))
env_path = "/app/.env"

env_config = Config(RepositoryEnv(env_path))

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : env_config.get('MYSQL_DATABASE'),
        'USER'    : env_config.get('MYSQL_USER'),
        'PASSWORD': env_config.get('MYSQL_PASSWORD'),
        'HOST'    : 'mysql_db',
        'PORT'    : '3306',
    }
}

DEBUG = True
SECRET_KEY = env_config.get('SECRET_KEY')
# ALLOWED_HOST = ['*']
AUTH_USER_MODEL = 'app.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'app',
    'proj'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proj.urls'

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

WSGI_APPLICATION = 'proj.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

CSRF_COOKIE_SECURE = False  # Set to True in production for HTTPS
CSRF_COOKIE_HTTPONLY = False # Set to True in production for security
CSRF_COOKIE_SAMESITE = None # Set to 'Lax' or 'Strict' if you need it
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000', 'http://localhost:5173', 'http://127.0.0.1:5173', 'http://127.0.0.1:4173', 'http://localhost:4173'] 

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    "http://svelte_frontend",
    "http://svelte_frontend:5173"
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-sveltekit-action",
]

# --- Email Settings (Mailjet) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env_config.get('EMAIL_HOST', default='in-v3.mailjet.com')
EMAIL_PORT = env_config.get('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = env_config.get('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = env_config.get('MAILJET_API_KEY', default='')
EMAIL_HOST_PASSWORD = env_config.get('MAILJET_SECRET_KEY', default='')
DEFAULT_FROM_EMAIL = env_config.get('DEFAULT_FROM_EMAIL', default='')
