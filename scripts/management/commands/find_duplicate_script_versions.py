from django.core.management.base import BaseCommand
from django.db.models import Count

from scripts.models import Script, ScriptVersion


class Command(BaseCommand):
    """
    Reports script versions that share the same (script, version) pair - see issue #503.

    This is read only. Deciding which duplicate to keep needs a human: they can differ in
    content, PDF, author, notes and tags, and the "losing" one isn't necessarily the one to
    delete. For each duplicate group this prints enough to tell them apart (pk, created
    date, latest flag, author, whether a PDF is attached, and how many characters are in the
    content) so a maintainer can pick the one to keep, e.g. from the Django admin or a shell.
    """

    help = "List script versions that share the same script and version number (issue #503)"

    def handle(self, *args, **options):
        duplicate_keys = (
            ScriptVersion.plain_objects.values("script_id", "version")
            .annotate(count=Count("pk"))
            .filter(count__gt=1)
            .order_by("script_id", "version")
        )

        if not duplicate_keys:
            self.stdout.write(self.style.SUCCESS("No duplicate (script, version) pairs found."))
            return

        for key in duplicate_keys:
            script = Script.objects.get(pk=key["script_id"])
            versions = ScriptVersion.plain_objects.filter(script=script, version=key["version"]).order_by("pk")

            self.stdout.write(
                self.style.WARNING(
                    f"\n'{script.name}' (script ID: {script.pk}) has {key['count']} versions numbered {key['version']}:"
                )
            )
            for version in versions:
                self.stdout.write(
                    f"  - version ID {version.pk}: created {version.created:%Y-%m-%d %H:%M}, "
                    f"latest={version.latest}, author={version.author or '(none)'}, "
                    f"pdf={'yes' if version.pdf else 'no'}, {len(version.content)} content entries"
                )

        self.stdout.write(
            self.style.WARNING(
                f"\n{len(duplicate_keys)} duplicate (script, version) pair(s) found. "
                "Review each one and keep whichever version has the content that should survive, "
                "e.g. `ScriptVersion.plain_objects.get(pk=<id to remove>).delete()` in `manage.py shell`, "
                "then confirm only one version per (script, version) remains flagged latest."
            )
        )
