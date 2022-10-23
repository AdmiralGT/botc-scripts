from rest_framework import serializers

from scripts import models


# Serializers define the API representation.
class ScriptSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="script.name")
    score = serializers.ReadOnlyField(source="votes.count")

    class Meta:
        model = models.ScriptVersion
        fields = ["pk", "name", "version", "author", "content", "score"]


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Translation
        fields = [
            "character_name",
            "ability",
            "first_night_reminder",
            "other_night_reminder",
            "global_reminders",
            "reminders",
        ]
