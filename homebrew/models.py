from scripts import models as s_models
from django.db import models

# Note, if more Editions are added, the Script Upload view
# needs updating to bail out on the latest edition.
class Homebrewiness(models.IntegerChoices):
    HYBRID = 0, "Hybrid"
    HOMEBREW = 1, "Homebrew"

class HomebrewCharacterType(models.TextChoices):
    TOWNSFOLK = "Townsfolk"
    OUTSIDER = "Outsider"
    MINION = "Minion"
    DEMON = "Demon"
    TRAVELLER = "Traveller"
    FABLED = "Fabled"
    UNKNOWN = "Unknown"

class HomebrewCharacter(s_models.BaseCharacter):
    """
    Model for homebrew characters.

    The BaseCharacter class has all the information required but we override the character_type
    to allow for unknown character types (I don't think character type means anything to the app).
    """
    character_type = models.CharField(max_length=30, choices=HomebrewCharacterType.choices)

class HomebrewVersion(s_models.BaseVersion):
    """
    Model for Homebrew and Hybrid scripts.
    """
    script = models.ForeignKey(
        s_models.Script, on_delete=models.CASCADE, related_name="homebrew_versions"
    )
    homebrewiness = models.IntegerField(choices=Homebrewiness.choices, default=Homebrewiness.HOMEBREW)

