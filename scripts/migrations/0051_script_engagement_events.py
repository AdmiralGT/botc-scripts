import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scripts", "0050_remove_script_script_name_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="script",
            name="popularity_tracking_started_at",
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.CreateModel(
            name="ScriptEngagementEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("vote_added", "Vote added"),
                            ("vote_removed", "Vote removed"),
                            ("favourite_added", "Favourite added"),
                            ("favourite_removed", "Favourite removed"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "script",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="engagement_events",
                        to="scripts.script",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="scriptengagementevent",
            index=models.Index(fields=["created_at"], name="engagement_created_idx"),
        ),
        migrations.AddIndex(
            model_name="scriptengagementevent",
            index=models.Index(fields=["script", "created_at"], name="engagement_script_time_idx"),
        ),
    ]
