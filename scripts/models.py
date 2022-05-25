from django.contrib.auth.models import User
from django.db import models
from versionfield import VersionField

from scripts.managers import ScriptViewManager, CollectionManager


class Edition(models.TextChoices):
    BASE = "Base"
    KICKSTARTER = "+ Kickstarter"
    UNRELEASED = "+ Unreleased"


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


class ScriptTag(models.Model):
    """
    Tags that can be applied to a script.
    """

    name = models.CharField(max_length=30)
    public = models.BooleanField(default=False)
    style = models.CharField(
        max_length=20, choices=TagStyles.choices, default=TagStyles.BLUE
    )

    def __str__(self):
        return f"{self.name}"


class Script(models.Model):
    """
    A named script that can have multiple ScriptVersions
    """

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, related_name="+"
    )

    def latest_version(self):
        return self.versions.last()

    def __str__(self):
        return f"{self.pk}. {self.name}"


def determine_script_location(instance, filename):
    return f"{instance.script.pk}/{instance.version}/{filename}"


class ScriptVersion(models.Model):
    """
    Actual script model, tracking type, author, JSON, PDF etc.
    """

    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="versions"
    )
    latest = models.BooleanField(default=True)
    script_type = models.CharField(
        max_length=20, choices=ScriptTypes.choices, default=ScriptTypes.FULL
    )
    author = models.CharField(max_length=100, null=True, blank=True)
    version = VersionField()
    content = models.JSONField()
    pdf = models.FileField(null=True, blank=True, upload_to=determine_script_location)
    tags = models.ManyToManyField(ScriptTag, blank=True)
    created = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    objects = ScriptViewManager()

    def __str__(self):
        return f"{self.pk}. {self.script.name} - v{self.version}"


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


class Play(models.Model):
    """
    Model for a user to track plays on a script.
    """

    script = models.ForeignKey(
        ScriptVersion, on_delete=models.CASCADE, related_name="plays"
    )
    playtime = models.DateField(blank=True, auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plays")


class WorldCup(models.Model):
    """
    Model for displaying World Cup data.
    """

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
