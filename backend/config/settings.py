from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", default=False)

AUTH_USER_MODEL = "utilisateurs.Utilisateur"

ALLOWED_HOSTS =env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework_simplejwt",
    "rest_framework",
    "corsheaders",
    "apps.core",
    "apps.utilisateurs",
    "apps.parcelles",
    "apps.missions",
    "apps.communication",
    "apps.mesures",
    "apps.analyse",
    "apps.incidents",
    "apps.irrigation",
    "apps.dashboard",
]

SIMPLE_JWT = {
    "USER_ID_FIELD": "utilisateur_id",
    "USER_ID_CLAIM": "user_id",
}

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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
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
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("BASE_NOM"),
        "USER": env("BASE_UTILISATEUR"),
        "PASSWORD": env("BASE_MOT_DE_PASSE"),
        "HOST": env("BASE_HOTE", default="localhost"),
        "PORT": env("BASE_PORT", default="5432"),
    }
}



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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication",],
    "EXCEPTION_HANDLER": "apps.core.exceptions.gestionnaire_exceptions",
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])

CLE_ROBOT = env("CLE_ROBOT", default="")   # vide = tous les appels du robot sont refusés

DUREE_MAX_IRRIGATION_SECONDES = env.int("DUREE_MAX_IRRIGATION_SECONDES", default=300)  # RG18
AGE_MAX_MESURE_SECONDES = env.int("AGE_MAX_MESURE_SECONDES", default=1800)


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
