from django.core.management.base import BaseCommand
from scripts.models import Script


class Command(BaseCommand):
    help = "Find and delete Script objects that have no associated ScriptVersion objects"

    def handle(self, *args, **options):
        # Find all scripts with no versions
        orphaned_scripts = Script.objects.filter(versions__isnull=True)
        total = orphaned_scripts.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned scripts found!"))
            return

        self.stdout.write(f"Found {total} script(s) with no versions:\n")

        for script in orphaned_scripts:
            info = f"  ID: {script.pk} | Name: {script.name}"
            if script.owner:
                info += f" | Owner: {script.owner.username}"
            else:
                info += " | Owner: None"
            
            self.stdout.write(info)

        deleted_count, _ = orphaned_scripts.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} orphaned script(s)"))