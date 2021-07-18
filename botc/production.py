from .settings import *
import os

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ.get("DJANGO_HOST", None)]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", False) == "True"

# DBHOST is only the server name, not the full URL
hostname = os.environ.get("DBHOST")

# Configure Postgres database; the full username is username@servername,
# which we construct using the DBHOST value.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DBNAME"),
        "HOST": hostname + ".postgres.database.azure.com",
        "USER": os.environ.get("DBUSER") + "@" + hostname,
        "PASSWORD": os.environ.get("DBPASS"),
    }
}


AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME", "botcscripts")
AZURE_CUSTOM_DOMAIN = os.environ.get("AZURE_CDN_DOMAIN")
AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY", False)
AZURE_SSL = True

DEFAULT_FILE_STORAGE = "botc.storage.AzureMediaStorage"
AZURE_MEDIA_CONTAINER = os.environ.get("AZURE_MEDIA_CONTAINER", "media")
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/"

STATICFILES_STORAGE = "botc.storage.AzureStaticStorage"
AZURE_STATIC_CONTAINER = os.environ.get("AZURE_STATIC_CONTAINER", "static")
STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, AZURE_ACCOUNT_NAME, AZURE_STATIC_CONTAINER)]