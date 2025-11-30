from django.core.management.base import BaseCommand
from scripts.models import ScriptVersion
from scripts.views import create_characters_and_determine_homebrew_status


class Command(BaseCommand):
    help = "Update homebrewiness field for all script versions (Clocktower/Hybrid/Homebrew)"

    def handle(self, *args, **options):
        scripts = ScriptVersion.objects.all()
        total = scripts.count()
        updated_count = 0
        self.stdout.write(f"Processing {total} script versions...")

        for i, script_version in enumerate(scripts, 1):
            old_homebrewiness = script_version.homebrewiness

            # Calculate the new homebrewiness value
            new_homebrewiness = create_characters_and_determine_homebrew_status(
                script_version.content, script_version.script
            )

            if old_homebrewiness != new_homebrewiness:
                updated_count += 1
                script_version.homebrewiness = new_homebrewiness
                script_version.save(update_fields=["homebrewiness"])

                self.stdout.write(
                    f"  [{i}/{total}] {script_version.script.name} v{script_version.version}: "
                    f"{old_homebrewiness} -> {new_homebrewiness}"
                )

            if i % 100 == 0:
                self.stdout.write(f"Progress: {i}/{total} ({updated_count} updates)")

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {updated_count} script versions"))
