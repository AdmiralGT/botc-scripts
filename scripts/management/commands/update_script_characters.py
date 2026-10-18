from django.core.management.base import BaseCommand

from scripts.models import ScriptVersion, sync_script_version_characters


class Command(BaseCommand):
    help = "Rebuild the denormalised character index for all script versions"

    def handle(self, *args, **options):
        scripts = ScriptVersion.objects.all()
        total = scripts.count()

        self.stdout.write(f"Updating {total} script versions...")

        for i, script in enumerate(scripts.iterator(chunk_size=500), 1):
            sync_script_version_characters(script)

            if i % 100 == 0:
                self.stdout.write(f"Progress: {i}/{total}")

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {total} script versions"))
