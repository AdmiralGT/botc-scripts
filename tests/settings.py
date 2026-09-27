"""Django settings used by pytest (see DJANGO_SETTINGS_MODULE in pyproject.toml).

The models rely on PostgreSQL features (GinIndex, pg_trgm), so the tests need a
PostgreSQL database. Connection details can be overridden with the TEST_DB_*
environment variables; the defaults match the service used in CI.
"""

import os

from botc.settings import *

SECRET_KEY = "test-secret-key-not-for-production"

# Defined in botc.local / botc.production rather than the base settings.
UPLOAD_DISABLED = False
BANNER = None

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("TEST_DB_NAME", "postgres"),
        "HOST": os.environ.get("TEST_DB_HOST", "localhost"),
        "PORT": os.environ.get("TEST_DB_PORT", "5432"),
        "USER": os.environ.get("TEST_DB_USER", "postgres"),
        "PASSWORD": os.environ.get("TEST_DB_PASSWORD", "postgres"),
    }
}
