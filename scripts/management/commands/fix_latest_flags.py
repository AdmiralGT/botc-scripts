from django.core.management.base import BaseCommand
from scripts.models import Script


class Command(BaseCommand):
    help = "Fix the 'latest' flag for script versions - ensures the highest version has latest=True"

    def handle(self, *args, **options):
        scripts = Script.objects.all()
        total = scripts.count()
        
        self.stdout.write(f"Processing {total} scripts...")

        updated_count = 0
        scripts_with_issues = []

        for i, script in enumerate(scripts, 1):
            latest_version = script.latest_version()
            
            if not latest_version:
                # No versions at all for this script
                self.stdout.write(
                    self.style.WARNING(f"  [{i}/{total}] Script '{script.name}' (ID: {script.pk}) has no versions")
                )
                continue
            
            # Check if the latest version has the latest flag set
            if not latest_version.latest:
                updated_count += 1
                scripts_with_issues.append({
                    'script': script,
                    'version': latest_version
                })
                
                self.stdout.write(
                    f"  [{i}/{total}] '{script.name}' v{latest_version.version} "
                    f"(ID: {latest_version.pk}) - latest flag is False, should be True"
                )
                
                latest_version.latest = True
                latest_version.save(update_fields=['latest'])
            
            # Also check if there are other versions incorrectly marked as latest
            other_versions = script.versions.exclude(pk=latest_version.pk).filter(latest=True)
            if other_versions.exists():
                for other_version in other_versions:
                    updated_count += 1
                    
                    self.stdout.write(
                        f"  [{i}/{total}] '{script.name}' v{other_version.version} "
                        f"(ID: {other_version.pk}) - latest flag is True, should be False"
                    )
                    
                    other_version.latest = False
                    other_version.save(update_fields=['latest'])
            
            if (i % 100 == 0):
                self.stdout.write(f"Progress: {i}/{total} ({updated_count} updates)")

        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"Total scripts processed: {total}")
        self.stdout.write(f"Script versions updated: {updated_count}")
        
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully fixed {updated_count} script version(s)"))
