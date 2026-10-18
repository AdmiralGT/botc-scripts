from itertools import islice

from django.core.management.base import BaseCommand

from scripts.models import ClocktowerCharacter, HomebrewCharacter, Homebrewiness, ScriptTag, ScriptVersion
from scripts.views import create_characters_and_determine_homebrew_status

HYBRID_TAG_ID = 49
HOMEBREW_TAG_ID = 50
HOMEBREW_CHARACTER_UPDATE_FIELDS = [
    "script",
    "character_name",
    "image_url",
    "character_type",
    "ability",
    "first_night_position",
    "other_night_position",
    "first_night_reminder",
    "other_night_reminder",
    "global_reminders",
    "reminders",
    "modifies_setup",
]


class Command(BaseCommand):
    help = "Update homebrewiness field and Hybrid/Homebrew tags for all script versions"
    batch_size = 100

    def handle(self, *args, **options):
        scripts = (
            ScriptVersion.plain_objects.only("pk", "content", "homebrewiness", "version", "script_id", "script__name")
            .select_related("script")
            .prefetch_related("tags")
        )
        total = scripts.count()
        updated_count = 0
        tag_updated_count = 0
        self.stdout.write(f"Processing {total} script versions...")

        clocktower_character_types = dict(ClocktowerCharacter.objects.values_list("character_id", "character_type"))
        hybrid_tag = ScriptTag.objects.filter(pk=HYBRID_TAG_ID).first()
        homebrew_tag = ScriptTag.objects.filter(pk=HOMEBREW_TAG_ID).first()

        scripts_iterator = scripts.iterator(chunk_size=self.batch_size)
        processed = 0
        while batch := list(islice(scripts_iterator, self.batch_size)):
            updated_versions = []
            homebrew_character_updates = {}

            for offset, script_version in enumerate(batch, processed + 1):
                old_homebrewiness = script_version.homebrewiness
                new_homebrewiness = create_characters_and_determine_homebrew_status(
                    script_version.content,
                    script_version.script,
                    clocktower_character_types=clocktower_character_types,
                    homebrew_character_updates=homebrew_character_updates,
                )

                if old_homebrewiness != new_homebrewiness:
                    updated_count += 1
                    script_version.homebrewiness = new_homebrewiness
                    updated_versions.append(script_version)
                    self.stdout.write(
                        f"  [{offset}/{total}] {script_version.script.name} v{script_version.version}: "
                        f"{old_homebrewiness} -> {new_homebrewiness}"
                    )

                existing_tag_ids = {tag.pk for tag in script_version.tags.all()}
                tags_changed = False
                if hybrid_tag:
                    if new_homebrewiness == Homebrewiness.HYBRID:
                        if HYBRID_TAG_ID not in existing_tag_ids:
                            script_version.tags.add(hybrid_tag)
                            tags_changed = True
                    elif HYBRID_TAG_ID in existing_tag_ids:
                        script_version.tags.remove(hybrid_tag)
                        tags_changed = True

                if homebrew_tag:
                    if new_homebrewiness == Homebrewiness.HOMEBREW:
                        if HOMEBREW_TAG_ID not in existing_tag_ids:
                            script_version.tags.add(homebrew_tag)
                            tags_changed = True
                    elif HOMEBREW_TAG_ID in existing_tag_ids:
                        script_version.tags.remove(homebrew_tag)
                        tags_changed = True

                if tags_changed:
                    tag_updated_count += 1
                    self.stdout.write(
                        f"  [{offset}/{total}] {script_version.script.name} v{script_version.version}: tags updated"
                    )

            if updated_versions:
                ScriptVersion.plain_objects.bulk_update(updated_versions, ["homebrewiness"], batch_size=self.batch_size)
            if homebrew_character_updates:
                HomebrewCharacter.objects.bulk_create(
                    list(homebrew_character_updates.values()),
                    update_conflicts=True,
                    update_fields=HOMEBREW_CHARACTER_UPDATE_FIELDS,
                    unique_fields=["character_id"],
                    batch_size=1000,
                )

            processed += len(batch)

            if processed % self.batch_size == 0:
                self.stdout.write(f"Progress: {processed}/{total} ({updated_count} homebrewiness updates)")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully updated {updated_count} script versions' homebrewiness "
                f"and {tag_updated_count} script versions' tags"
            )
        )
