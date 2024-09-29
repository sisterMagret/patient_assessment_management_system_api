from .base import *

DEBUG = False

DATABASES = {
    "default": {
        "NAME": config("DATABASE_NAME"),
        "ENGINE": config("DATABASE_ENGINE"),
        "USER": config("DATABASE_USER"),
        "PORT": config("DATABASE_PORT"),
        "PASSWORD": config("DATABASE_PASSWORD"),
    }
}


# EMAIL SETTINGS
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
