import os

from .settings import * # noqa

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = os.environ.get("DJANGO_HOST", None).split(" ")

CSRF_TRUSTED_ORIGINS = [
    "https://botcscripts.com",
    "https://botc-scripts.azurewebsites.net",
    "https://www.botcscripts.com",
]

SECRET_KEY = os.environ.get("SECRET_KEY")

# Settings configurable via Environment Variables
DEBUG = os.environ.get("DEBUG", False) == "True"
UPLOAD_DISABLED = os.environ.get("UPLOAD_DISABLED", False) == "True"
DISABLE_VALIDATORS = os.environ.get("DISABLE_VALIDATORS", False) == "True"
BANNER = os.environ.get('BANNER', None)

# DBHOST is only the server name, not the full URL
hostname = os.environ.get("DBHOST")

# Configure Postgres database; the full username is username@servername,
# which we construct using the DBHOST value.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DBNAME"),
        "HOST": hostname + ".postgres.database.azure.com",
        "USER": os.environ.get("DBUSER"),
        "PASSWORD": os.environ.get("DBPASS"),
    }
}


AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME", "botcscripts")
AZURE_CUSTOM_DOMAIN = os.environ.get("AZURE_CDN_DOMAIN")
AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY", False)
AZURE_SSL = True

STORAGES = {
    "default": {
        "BACKEND": "botc.storage.AzureMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "botc.storage.AzureStaticStorage",
    },
}

AZURE_MEDIA_CONTAINER = os.environ.get("AZURE_MEDIA_CONTAINER", "media")
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/"

AZURE_STATIC_CONTAINER = os.environ.get("AZURE_STATIC_CONTAINER", "static")
STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles") # noqa
BS_ICONS_CACHE = os.path.join(STATIC_ROOT, "icon_cache")

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
            "redirect_uri": "https://www.botcscripts.com/google/login/callback/",
        },
        "APP": {
            "client_id": os.getenv("GOOGLE_OAUTH2_CLIENT_ID", None),
            "secret": os.getenv("GOOGLE_OAUTH2_SECRET", None),
            "key": "",
        },
    },
    "discord": {
        "SCOPE": [
            "email",
            "identify",
        ],
        "AUTH_PARAMS": {
            "redirect_uri": "https://www.botcscripts.com/discord/login/callback/",
        },
        "APP": {
            "client_id": os.getenv("DISCORD_OAUTH2_CLIENT_ID", None),
            "secret": os.getenv("DISCORD_OAUTH2_SECRET", None),
            "key": "",
        },
    },
}

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')