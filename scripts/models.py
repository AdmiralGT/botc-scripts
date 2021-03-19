from django.db import models
from django.contrib.auth.models import User
from versionfield import VersionField


class ScriptTypes(models.TextChoices):
    TEENSYVILLE = "Teensyville"
    RAVENSWOOD = "Ravenswood Bluff"
    PHOBOS = "Phobos"


# Create your models here.
class Script(models.Model):
    name = models.CharField(max_length=100)

    def latest_version(self):
        return self.versions.last()


class ScriptVersion(models.Model):
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="versions"
    )
    type = models.CharField(max_length=20, choices=ScriptTypes.choices, default=ScriptTypes.RAVENSWOOD)
    version = VersionField()
    content = models.JSONField()
    pdf = models.FileField(null=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    # Might want to have a parent field so can have threads
