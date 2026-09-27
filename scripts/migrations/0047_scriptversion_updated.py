import django.utils.timezone
from django.db import migrations, models


def backfill_updated(apps, schema_editor):
    # Existing versions have never had an edit time recorded, so the best available value is the upload time.
    # Note: ScriptVersion.created was auto_now (i.e. "last saved") until migration 0024 (April 2023), so for
    # versions last saved before then it is the last save time, not the true upload time.
    ScriptVersion = apps.get_model("scripts", "ScriptVersion")
    ScriptVersion.objects.update(updated=models.F("created"))


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0046_scriptversion_sv_content_gin_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='scriptversion',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunPython(backfill_updated, migrations.RunPython.noop),
    ]
