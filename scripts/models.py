from django.db import models
from django.contrib.auth.models import User
from versionfield import VersionField
from .managers import ScriptViewManager


class ScriptTypes(models.TextChoices):
    TEENSYVILLE = "Teensyville"
    FULL = "Full"


class Script(models.Model):
    name = models.CharField(max_length=100)

    def latest_version(self):
        return self.versions.last()

    def __str__(self):
        return self.name


def determine_script_location(instance, filename):
    return f"{instance.script.pk}/{instance.version}/{filename}"


class ScriptVersion(models.Model):
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="versions"
    )
    latest = models.BooleanField(default=True)
    type = models.CharField(
        max_length=20, choices=ScriptTypes.choices, default=ScriptTypes.FULL
    )
    author = models.CharField(max_length=100, null=True, blank=True)
    version = VersionField()
    content = models.JSONField()
    pdf = models.FileField(null=True, blank=True, upload_to=determine_script_location)

    objects = ScriptViewManager()

    def __str__(self):
        return f"{self.script.pk}. {self.script.name} - v{self.version}" 


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    # Might want to have a parent field so can have threads


class Vote(models.Model):
    script = models.ForeignKey(
        ScriptVersion, on_delete=models.CASCADE, related_name="votes"
    )
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk}. Vote on {self.script.script.name} version {self.script.version}"
