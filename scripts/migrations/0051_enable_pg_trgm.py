from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Enables the pg_trgm extension, required by the trigram (GIN) indexes added in the next
    migration that back the TrigramSimilarity search on script name and author.
    """

    dependencies = [
        ("scripts", "0050_remove_script_script_name_idx_and_more"),
    ]

    operations = [
        TrigramExtension(),
    ]
