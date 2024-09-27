from base import *

DEBUG=False

DATABASES = {
    "default": {
        "NAME": config("DB_NAME"),
        "ENGINE": config("DB_ENGINE"),
        "USER": config("DB_USER"),
        "PORT": config("DB_PORT"),
        "PASSWORD": config("DB_PASSWORD"),
    }
}

# EMAIL SETTINGS
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"