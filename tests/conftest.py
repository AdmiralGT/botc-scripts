from django.conf import settings

# CI runs with the empty tests.settings module and has no database, so the tests that need the project's apps and a
# PostgreSQL database are only collected when the real settings are in use, e.g.
#     uv run pytest --ds=botc.local
DATABASE_TESTS = ["test_advanced_search.py"]

collect_ignore = [] if "scripts.apps.ScriptsConfig" in settings.INSTALLED_APPS else DATABASE_TESTS
