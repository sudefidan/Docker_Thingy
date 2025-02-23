from decouple import Config, RepositoryEnv
from os import path, curdir

file_path = path.dirname(path.abspath(__file__))
env_path = path.join(file_path, "../.env")

env_config = Config(RepositoryEnv(env_path))

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : env_config.get('MYSQL_DATABASE'),
        'USER'    : env_config.get('MYSQL_USER'),
        'PASSWORD': env_config.get('MYSQL_PASSWORD'),
        'HOST'    : '127.0.0.1',
        'PORT'    : '3306',
    }
}

DEBUG = env_config.get('DEBUG')
SECRET_KEY = env_config.get('SECRET_KEY')
# ALLOWED_HOST = ['*']
ALLOWED_HOST = [
    '127.0.0.1',
    'localhost'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',  # Your Svelte frontend
    'http://127.0.0.1:5173',  # Alternative for the same host
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',  # Your Django app
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # ✅ Allow Svelte dev server
    "http://127.0.0.1:5173",
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