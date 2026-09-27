from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Enables the pg_trgm extension, required by the trigram (GIN) indexes added in the next
    migration that back the TrigramSimilarity search on script name and author.
    """

    dependencies = [
        ("scripts", "0046_scriptversion_sv_content_gin_idx"),
    ]

    operations = [
        TrigramExtension(),
    ]
