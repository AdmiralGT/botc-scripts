from django.db import migrations
from scripts.script_json import strip_special_characters

def update_character_ids(apps, _schema_editor):
    Character = apps.get_model("scripts", "character")
    Translation = apps.get_model("scripts", "translation")
    for character in Character.objects.all():
        character.character_id = strip_special_characters(character.character_id)

    for translation in Translation.objects.all():
        translation.character_id = strip_special_characters(translation.character_id)


class Migration(migrations.Migration):

    dependencies = [
        ("scripts", "0026_alter_scripttag_style"),
    ]

    operations = [
        
        migrations.RunPython(
            update_character_ids, reverse_code=migrations.RunPython.noop
        ),
    ]
