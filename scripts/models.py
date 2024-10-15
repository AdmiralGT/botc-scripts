from django.contrib.auth.models import User
from django.db import models
from versionfield import VersionField

from scripts import constants
from scripts.managers import ScriptViewManager, CollectionManager
from typing import Dict


# Note, if more Editions are added, the Script Upload view
# needs updating to bail out on the latest edition.
class Edition(models.IntegerChoices):
    BASE = 0, "Base"
    KICKSTARTER = 1, "Kickstarter"
    UNRELEASED = 2, "clocktower.online"
    CLOCKTOWER_APP = 3, "All"


class ScriptTypes(models.TextChoices):
    TEENSYVILLE = "Teensyville"
    FULL = "Full"


class TagStyles(models.TextChoices):
    BLUE = "badge-primary"
    GREY = "badge-secondary"
    GREEN = "badge-success"
    RED = "badge-danger"
    YELLOW = "badge-warning"
    CYAN = "badge-info"
    WHITE = "badge-light"
    BLACK = "badge-dark"
    PURPLE = "badge-purple"
    NOCTURNE = "badge-nocturne"


class CharacterType(models.TextChoices):
    TOWNSFOLK = "Townsfolk"
    OUTSIDER = "Outsider"
    MINION = "Minion"
    DEMON = "Demon"
    TRAVELLER = "Traveller"
    FABLED = "Fabled"


class ScriptTag(models.Model):
    """
    Tags that can be applied to a script.
    """

    name = models.CharField(max_length=100)
    public = models.BooleanField(default=False)
    style = models.CharField(
        max_length=20, choices=TagStyles.choices, default=TagStyles.BLUE
    )
    order = models.IntegerField(unique=True)
    inheritable = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class Script(models.Model):
    """
    A named script that can have multiple ScriptVersions
    """

    name = models.CharField(max_length=constants.MAX_SCRIPT_NAME_LENGTH)
    owner = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, related_name="+"
    )

    def latest_version(self):
        return self.versions.order_by("-version").first()

    def __str__(self):
        return f"{self.pk}. {self.name}"


def determine_script_location(instance, filename):
    return f"{instance.script.pk}/{instance.version}/{filename}"


class BaseVersion(models.Model):
    """
    Actual script model, tracking type, author, JSON, PDF etc.
    """

    latest = models.BooleanField(default=True)
    script_type = models.CharField(
        max_length=20, choices=ScriptTypes.choices, default=ScriptTypes.FULL
    )
    author = models.CharField(
        max_length=constants.MAX_AUTHOR_NAME_LENGTH, null=True, blank=True
    )
    version = VersionField()
    content = models.JSONField()
    pdf = models.FileField(null=True, blank=True, upload_to=determine_script_location)
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    num_townsfolk = models.IntegerField()
    num_outsiders = models.IntegerField()
    num_minions = models.IntegerField()
    num_demons = models.IntegerField()
    num_fabled = models.IntegerField()
    num_travellers = models.IntegerField()

    def __str__(self):
        return f"{self.pk}. {self.script.name} - v{self.version}"
    
    class Meta:
        abstract = True


class ScriptVersion(BaseVersion):
    """
    Actual script model, tracking type, author, JSON, PDF etc.
    """
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="clocktower_versions"
    )
    tags = models.ManyToManyField(ScriptTag, blank=True)
    edition = models.IntegerField(choices=Edition.choices, default=Edition.BASE)

    objects = ScriptViewManager()

    class Meta:
        permissions = [
            (
                "download_unsupported_json",
                "Can the request the download of a JSON that replaces unsupported characters",
            )
        ]


class Comment(models.Model):
    """
    Model for commenting on scripts. Comments are only allowed by authenticated users.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    # Might want to have a parent field so can have threads


class Vote(models.Model):
    """
    Model for tracking votes on scripts indicating how popular they are.

    Only authenticated users may vote for scripts.
    """

    script = models.ForeignKey(
        ScriptVersion, on_delete=models.CASCADE, related_name="votes"
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="votes"
    )

    def __str__(self):
        return f"{self.pk}. Vote on {self.script.script.name} version {self.script.version}"


class Favourite(models.Model):
    """
    Model for tracking a user's favourite scripts.

    Only authenticated users may have favourite scripts.
    """

    script = models.ForeignKey(
        ScriptVersion, on_delete=models.CASCADE, related_name="favourites"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favourites")


class WorldCup(models.Model):
    """
    Model for displaying World Cup data.
    """

    winner_choices = [("Unknown", "Unknown"), ("Home", "Home"), ("Away", "Away")]

    round = models.IntegerField()
    script1 = models.ForeignKey(
        ScriptVersion,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    script2 = models.ForeignKey(
        ScriptVersion,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    vod = models.CharField(max_length=100, blank=True)
    form = models.CharField(max_length=100, blank=True)
    winner = models.CharField(max_length=10, choices=winner_choices, default="Unknown")


class Collection(models.Model):
    """
    Model for collections, a shareable set of scripts.
    """

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collections"
    )
    scripts = models.ManyToManyField(
        ScriptVersion, blank=True, related_name="collections"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, max_length=255)
    notes = models.TextField(null=True, blank=True)

    objects = CollectionManager()


class BaseCharacterInfo(models.Model):
    """
    Abstract model used to describe a character and translation information.
    """

    character_id = models.CharField(max_length=30)
    character_name = models.CharField(max_length=30)
    ability = models.TextField()
    first_night_reminder = models.TextField(blank=True, null=True)
    other_night_reminder = models.TextField(blank=True, null=True)
    global_reminders = models.CharField(max_length=30, blank=True, null=True)
    reminders = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class BaseCharacter(BaseCharacterInfo):
    character_type = models.CharField(max_length=30, choices=CharacterType.choices)
    first_night_position = models.FloatField(blank=True, null=True)
    other_night_position = models.FloatField(blank=True, null=True)
    image_url = models.CharField(blank=True, null=True, max_length=100)
    modifies_setup = models.BooleanField(default=False)

    def full_character_json(self) -> Dict:
        character_json = {}
        character_json["id"] = self.character_id
        character_json["name"] = self.character_name
        character_json["team"] = self.character_type.lower()
        character_json["firstNight"] = self.first_night_position
        character_json["firstNightReminder"] = self.first_night_reminder
        character_json["otherNight"] = self.other_night_position
        character_json["otherNightReminder"] = (
            self.other_night_reminder if self.other_night_reminder else ""
        )
        character_json["reminders"] = self.reminders.split(",")
        character_json["setup"] = self.modifies_setup
        character_json["ability"] = self.ability
        character_json["image"] = self.image_url
        return character_json

    def __str__(self):
        return f"{self.character_name}"

    class Meta:
        abstract = True

class Character(BaseCharacter):
    """
    Model for characters.
    """
    edition = models.IntegerField(choices=Edition.choices)

    class Meta:
        permissions = [("update_characters", "Can update character information")]


class Translation(BaseCharacterInfo):
    """
    Model for translations of characters.
    """

    language = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["language", "character_id"], name="character_language"
            )
        ]
        indexes = [
            models.Index(fields=["language", "character_id"]),
        ]
        permissions = [("update_translation", "Can update a translation")]

    def full_character_json(self) -> Dict:
        character_json = {}
        character_json["id"] = f"{self.language}_{self.character_id}"
        character_json["name"] = self.character_name
        character_json["firstNightReminder"] = self.first_night_reminder
        character_json["otherNightReminder"] = (
            self.other_night_reminder if self.other_night_reminder else ""
        )
        character_json["reminders"] = (
            self.reminders.split(",") if self.reminders else []
        )
        character_json["ability"] = self.ability
        return character_json

    def __str__(self):
        return f"{self.language} - {self.character_id}"
