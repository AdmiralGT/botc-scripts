from django.core.management.base import BaseCommand
from scripts.models import ScriptVersion, CharacterType
from scripts.views import count_character


class Command(BaseCommand):
    help = "Update character count fields for all script versions"

    def handle(self, *args, **options):
        scripts = ScriptVersion.objects.all()
        total = scripts.count()

        self.stdout.write(f"Updating {total} script versions...")

        for i, script in enumerate(scripts, 1):
            script.num_townsfolk = count_character(script.content, CharacterType.TOWNSFOLK)
            script.num_outsiders = count_character(script.content, CharacterType.OUTSIDER)
            script.num_minions = count_character(script.content, CharacterType.MINION)
            script.num_demons = count_character(script.content, CharacterType.DEMON)
            script.num_fabled = count_character(script.content, CharacterType.FABLED)
            script.num_loric = count_character(script.content, CharacterType.LORIC)
            script.num_travellers = count_character(script.content, CharacterType.TRAVELLER)
            script.save()

            if i % 100 == 0:
                self.stdout.write(f"Progress: {i}/{total}")

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {total} script versions"))
