from scripts import models as s_models
from django.db import models

# Note, if more Editions are added, the Script Upload view
# needs updating to bail out on the latest edition.
class Homebrewiness(models.IntegerChoices):
    HYBRID = 0, "Hybrid"
    HOMEBREW = 1, "Homebrew"


class HomebrewCharacter(s_models.BaseCharacter):
    """
    Model for homebrew characters.

    The BaseCharacter class has all the information required in currently, but is an abstract
    class in case we want to change the inheritence hierarchy.
    """
    pass

class HomebrewVersion(s_models.BaseVersion):
    """
    Model for Homebrew and Hybrid scripts.
    """
    script = models.ForeignKey(
        s_models.Script, on_delete=models.CASCADE, related_name="homebrew_versions"
    )
    homebrewiness = models.IntegerField(choices=Homebrewiness.choices, default=Homebrewiness.HOMEBREW)

