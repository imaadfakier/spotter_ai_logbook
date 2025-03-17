"""
Django settings for spotter_ai_trucker_logbook project.
"""

import os  # Import the os module
from pathlib import Path
import dj_database_url
import os
from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
# os.environ.get("DJANGO_SECRET_KEY", "xxxxxxxxxxxxx")
# utils.get_random_secret_key()) - can set automatically
# check in local environment. Do not commit it.

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG")

ALLOWED_HOSTS = ["*"]  # os.environ.get('ALLOWED_HOSTS').split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "trucker_logbook",  # Make sure your app is installed
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "spotter_ai_trucker_logbook.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "spotter_ai_trucker_logbook.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}
# The configuration will work if we are not relying on external libraries, but for deployment
# If you use dj_database_url, it will use that for local

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS settings
CORS_ORIGIN_ALLOW_ALL = False  # Change to True only for development
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",  # Replace with your React frontend's origin
    "http://localhost:8000",
    "https://spotter-ai-logbook-react-frontend.vercel.app"
]
