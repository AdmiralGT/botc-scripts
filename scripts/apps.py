from django.apps import AppConfig


class ScriptsConfig(AppConfig):
    name = "scripts"

    def ready(self):
        from scripts import signals  # noqa: F401
