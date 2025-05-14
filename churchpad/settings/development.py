from .base import *  # noqa
from .base import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="oXPWQPA3C3sdBCuBeXUKq3LBp9YDJ33-306p9EAKf1ja1xkWnKY",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://0.0.0.0:8000",
    "http://0.0.0.0:8080"
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
]

CORS_ALLOWED_ORIGINS = [
    "http://0.0.0.0:8000",
    "http://0.0.0.0:8080",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    " http://localhost:5173",
]


EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env("EMAIL_PORT", default="1025")
DEFAULT_FROM_EMAIL = "tankoraphael6@gmail.com"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)
DOMAIN = env("DOMAIN", default="localhost")
SITE_NAME = "churchpad"
