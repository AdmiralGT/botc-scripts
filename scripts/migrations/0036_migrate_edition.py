from django.db import migrations, models

def change_edition(apps, _):
    from scripts import models, views
    ClocktowerCharacter = apps.get_model("scripts", "clocktowercharacter")
    ScriptVersion = apps.get_model("scripts", "scriptversion")
    
    # Update existing clocktower characters to have the correct edition choices
    for character in ClocktowerCharacter.objects.all():
        if character.edition == models.Edition.ALL:
            character.edition == models.Edition.CAROUSEL
            character.save()

    # Update existing script versions to have the correct edition choices
    for version in ScriptVersion.objects.all():
        version.edition = views.calculate_edition(version.content)
        version.save()

def remove_duplicate_votes_and_favourites(apps, _):
    Vote = apps.get_model("scripts", "vote")
    Favourite = apps.get_model("scripts", "favourite")
    Script = apps.get_model("scripts", "script")

    for script in Script.objects.all():
        VoteUsers = set()
        FavouriteUsers = set()
        for Vote in script.votes.all():
            if Vote.user in VoteUsers:
                Vote.delete()
            else:
                VoteUsers.add(Vote.user)
        for Favourite in script.favourites.all():
            if Favourite.user in FavouriteUsers:
                Favourite.delete()
            else:
                FavouriteUsers.add(Favourite.user)
            
            

class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0035_favourite_parent_vote_parent_and_more'),
    ]

    operations = [
        migrations.RunPython(
            change_edition,
            reverse_code=migrations.RunPython.noop,  # No reverse migration needed
        ),
        migrations.RunPython(
            remove_duplicate_votes_and_favourites,
            reverse_code=migrations.RunPython.noop,  # No reverse migration needed
        ),
    ]
