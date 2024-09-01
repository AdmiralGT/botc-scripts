from django.db import migrations, models

from scripts.views import count_character
from scripts.models import CharacterType


def update_character_ids(apps, _schema_editor):
    Character = apps.get_model("scripts", "character")
    Translation = apps.get_model("scripts", "translation")
    for character in Character.objects.all():
        character.character_id = character.character_id.replace("_","").replace("-","")

    for translation in Translation.objects.all():
        translation.character_id = translation.character_id.replace("_", "").replace("-", "")


class Migration(migrations.Migration):

    dependencies = [
        ("scripts", "0026_alter_scripttag_style"),
    ]

    operations = [
        
        migrations.RunPython(
            update_character_ids, reverse_code=migrations.RunPython.noop
        ),
    ]
