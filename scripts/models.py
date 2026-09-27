from pathlib import Path
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import F, Value, Window
from django.db.models.functions import Cast, Round, RowNumber
from versionfield import VersionField

from scripts import constants
from scripts.character_mask import MASK_BITS, BitAnd, BitCount, build_mask
from scripts.managers import CollectionManager, ScriptViewManager


# Note, if more Editions are added, the Script Upload view
# needs updating to bail out on the latest edition.
class Edition(models.IntegerChoices):
    BASE = 0, "Base"
    KICKSTARTER = 1, "Kickstarter"
    CAROUSEL = 2, "Carousel"
    ALL = 3, "All"


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
    BLOODRED = "badge-bloodred"
    CLOCKCONAUS = "badge-clockconaus"


class CharacterType(models.TextChoices):
    TOWNSFOLK = "Townsfolk"
    OUTSIDER = "Outsider"
    MINION = "Minion"
    DEMON = "Demon"
    TRAVELLER = "Traveller"
    FABLED = "Fabled"
    LORIC = "Loric"
    UNKNOWN = "Unknown"


CORE_CHARACTER_TYPES = (CharacterType.TOWNSFOLK, CharacterType.OUTSIDER, CharacterType.MINION, CharacterType.DEMON)
SIMILARITY_CATEGORIES = ("identical", "containedIn", "contains", "full", "teensyville")


class CharacterMaskField(models.Field):
    def db_type(self, connection):
        return f"bit({MASK_BITS})"


class Homebrewiness(models.IntegerChoices):
    CLOCKTOWER = 0, "Clocktower"
    HYBRID = 1, "Hybrid"
    HOMEBREW = 2, "Homebrew"


class ScriptTag(models.Model):
    """
    Tags that can be applied to a script.
    """

    name = models.CharField(max_length=100)
    public = models.BooleanField(default=False)
    style = models.CharField(max_length=20, choices=TagStyles.choices, default=TagStyles.BLUE)
    order = models.IntegerField(unique=True)
    inheritable = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["name"], name="scripttag_name_idx"),
            models.Index(fields=["public"], name="scripttag_public_idx"),
            models.Index(fields=["inheritable"], name="scripttag_inheritable_idx"),
            models.Index(fields=["order"], name="scripttag_order_idx"),
        ]


class Script(models.Model):
    """
    A named Clocktower script that can have multiple ScriptVersions
    """

    name = models.CharField(max_length=constants.MAX_SCRIPT_NAME_LENGTH)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    num_downloads = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pk}. {self.name}"

    def latest_version(self):
        return self.versions.order_by("-version").first()

    class Meta:
        indexes = [
            models.Index(fields=["name"], name="script_name_idx"),
            models.Index(fields=["owner"], name="script_owner_idx"),
        ]


class ScriptVersion(models.Model):
    """
    Actual script model, tracking type, author, JSON, PDF etc.
    """

    def determine_script_location(instance, filename):
        # Add hash to filename to bust CDN cache
        name = Path(filename).stem
        ext = Path(filename).suffix
        file_hash = uuid4().hex[:8]
        unique_filename = f"{name}_{file_hash}{ext}"
        return f"{instance.script.pk}/{instance.version}/{unique_filename}"

    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="versions")
    pdf = models.FileField(null=True, blank=True, upload_to=determine_script_location)
    latest = models.BooleanField(default=True)
    script_type = models.CharField(max_length=20, choices=ScriptTypes.choices, default=ScriptTypes.FULL)
    author = models.CharField(max_length=constants.MAX_AUTHOR_NAME_LENGTH, null=True, blank=True)
    version = VersionField()
    content = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    num_townsfolk = models.IntegerField()
    num_outsiders = models.IntegerField()
    num_minions = models.IntegerField()
    num_demons = models.IntegerField()
    num_fabled = models.IntegerField()
    num_loric = models.IntegerField()
    num_travellers = models.IntegerField()
    tags = models.ManyToManyField(ScriptTag, blank=True)
    edition = models.IntegerField(choices=Edition.choices, default=Edition.ALL)
    homebrewiness = models.IntegerField(choices=Homebrewiness.choices, default=Homebrewiness.CLOCKTOWER)
    character_mask = CharacterMaskField(null=True, blank=True, editable=False)

    objects = ScriptViewManager()
    plain_objects = models.Manager()

    def __str__(self):
        return f"{self.pk}. {self.script.name} - v{self.version}"

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields is None or "content" in update_fields:
            self.character_mask = build_mask(self.content, ClocktowerCharacter.character_bit_index_mapping())
            if update_fields is not None:
                kwargs["update_fields"] = {*update_fields, "character_mask"}
        super().save(*args, **kwargs)

    def similar_scripts(self, per_category: int = 10):
        count = self.character_mask.count("1")
        return (
            self._similarity_candidates()
            .annotate(similarity=self._jaccard_similarity(count), category=self._similarity_category(count))
            .annotate(
                rank=Window(RowNumber(), partition_by=F("category"), order_by=[F("similarity").desc(), "script_id"])
            )
            .filter(rank__lte=per_category)
            .order_by("category", "rank")
            .values_list("category", "script_id", "script__name", Round(F("similarity") * 100))
        )

    def _similarity_candidates(self):
        mask = Cast(Value(self.character_mask), CharacterMaskField())
        return (
            ScriptVersion.plain_objects.filter(latest=True, homebrewiness=Homebrewiness.CLOCKTOWER)
            .exclude(script_id=self.script_id)
            .annotate(shared=BitCount(BitAnd("character_mask", mask)), total=BitCount("character_mask"))
            .filter(shared__gt=0)
        )

    @staticmethod
    def _jaccard_similarity(count: int):
        return Cast("shared", models.FloatField()) / (F("total") + count - F("shared"))

    @staticmethod
    def _similarity_category(count: int):
        return models.Case(
            models.When(shared=count, total=count, then=Value("identical")),
            models.When(shared=count, then=Value("containedIn")),
            models.When(shared=F("total"), then=Value("contains")),
            models.When(script_type=ScriptTypes.TEENSYVILLE, then=Value("teensyville")),
            default=Value("full"),
        )

    class Meta:
        permissions = [
            (
                "download_unsupported_json",
                "Can the request the download of a JSON that replaces unsupported characters",
            ),
            (
                "api_write_permission",
                "Can create, update or delete scripts via the API. This is not required for reading scripts.",
            ),
        ]
        indexes = [
            models.Index(fields=["script"], name="sv_script_idx"),
            models.Index(fields=["latest"], name="sv_latest_idx"),
            models.Index(fields=["homebrewiness"], name="sv_homebrewiness_idx"),
            models.Index(fields=["edition"], name="sv_edition_idx"),
            models.Index(fields=["num_demons"], name="sv_num_demons_idx"),
            models.Index(fields=["script", "version"], name="sv_script_and_version_idx"),
            models.Index(fields=["latest", "homebrewiness"], name="sv_latest_and_homebrew_idx"),
            GinIndex(fields=["content"], name="sv_content_gin_idx"),
        ]


class Comment(models.Model):
    """
    Model for commenting on scripts. Comments are only allowed by authenticated users.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="comments")
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

    parent = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="votes", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="votes")

    def __str__(self):
        return f"{self.pk}. Vote on {self.parent.name}"

    class Meta:
        unique_together = ("parent", "user")
        indexes = [
            models.Index(fields=["parent"], name="vote_parent_idx"),
            models.Index(fields=["user"], name="vote_user_idx"),
        ]


class Favourite(models.Model):
    """
    Model for tracking a user's favourite scripts.

    Only authenticated users may have favourite scripts.
    """

    parent = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="favourites", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favourites")

    def __str__(self):
        return f"{self.pk}. Favourite on {self.parent.name}"

    class Meta:
        unique_together = ("parent", "user")
        indexes = [
            models.Index(fields=["parent"], name="favourite_parent_idx"),
            models.Index(fields=["user"], name="favourite_user_idx"),
        ]


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

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    scripts = models.ManyToManyField(ScriptVersion, blank=True, related_name="collections")
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, max_length=255)
    notes = models.TextField(null=True, blank=True)

    objects = CollectionManager()


class BaseCharacterInfo(models.Model):
    """
    Abstract model used to describe a character and translation information.
    """

    character_id = models.CharField(max_length=50, primary_key=True)
    character_name = models.CharField(max_length=30)
    ability = models.TextField()
    first_night_reminder = models.TextField(blank=True, null=True)
    other_night_reminder = models.TextField(blank=True, null=True)
    global_reminders = models.TextField(blank=True, null=True)
    reminders = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class BaseCharacter(BaseCharacterInfo):
    character_type = models.CharField(max_length=30, choices=CharacterType.choices)
    first_night_position = models.FloatField(blank=True, null=True)
    other_night_position = models.FloatField(blank=True, null=True)
    modifies_setup = models.BooleanField(default=False)

    def full_character_json(self) -> dict:
        character_json = {}
        character_json["id"] = self.character_id
        character_json["name"] = self.character_name
        character_json["team"] = self.character_type.lower()
        character_json["firstNight"] = self.first_night_position
        character_json["firstNightReminder"] = self.first_night_reminder
        character_json["otherNight"] = self.other_night_position
        character_json["otherNightReminder"] = self.other_night_reminder if self.other_night_reminder else ""
        character_json["reminders"] = self.reminders.split(",")
        character_json["setup"] = self.modifies_setup
        character_json["ability"] = self.ability
        character_json["image"] = (
            f"https://raw.githubusercontent.com/tomozbot/botc-icons/refs/heads/main/PNG/{self.character_id}.png"
            if not hasattr(self, "image_url")
            else self.image_url
        )
        return character_json

    def __str__(self):
        return f"{self.character_name}"

    class Meta:
        abstract = True


class ClocktowerCharacter(BaseCharacter):
    """
    Model for characters.
    """

    edition = models.IntegerField(choices=Edition.choices)
    bit_index = models.PositiveSmallIntegerField(unique=True, null=True, blank=True, editable=False)

    @classmethod
    def character_bit_index_mapping(cls) -> dict[str, int]:
        characters = cls.objects.filter(character_type__in=CORE_CHARACTER_TYPES, bit_index__isnull=False)
        return dict(characters.values_list("character_id", "bit_index"))

    class Meta:
        permissions = [("update_characters", "Can update character information")]

        indexes = [
            models.Index(fields=["character_type"], name="cchar_character_type_idx"),
            models.Index(fields=["character_id"], name="cchar_character_id_idx"),
            models.Index(fields=["edition"], name="cchar_edition_idx"),
        ]


class HomebrewCharacter(BaseCharacter):
    """
    Model for characters.
    """

    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name="+", null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        permissions = [("update_characters", "Can update character information")]
        indexes = [
            models.Index(fields=["character_type"], name="hchar_character_type_idx"),
            models.Index(fields=["character_id"], name="hchar_character_id_idx"),
        ]


class Translation(BaseCharacterInfo):
    """
    Model for translations of characters.
    """

    character_id = models.CharField(max_length=50, primary_key=False)
    language = models.CharField(max_length=10)
    character_name = models.CharField(max_length=30)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["language", "character_id"], name="character_language")]
        indexes = [
            models.Index(fields=["language", "character_id"]),
        ]
        permissions = [("update_translation", "Can update a translation")]

    def full_character_json(self) -> dict:
        character_json = {}
        character_json["id"] = f"{self.language}_{self.character_id}"
        character_json["name"] = self.character_name
        character_json["firstNightReminder"] = self.first_night_reminder
        character_json["otherNightReminder"] = self.other_night_reminder if self.other_night_reminder else ""
        character_json["reminders"] = self.reminders.split(",") if self.reminders else []
        character_json["ability"] = self.ability
        return character_json

    def __str__(self):
        return f"{self.language} - {self.character_id}"
