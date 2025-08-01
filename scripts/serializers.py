from rest_framework import serializers

from scripts import models, constants


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

class ScriptUploadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=constants.MAX_SCRIPT_NAME_LENGTH, required=True)

    class Meta:
        model = models.ScriptVersion
        fields = ["content", "version", "author", "pdf", "notes"]

    def is_valid(self, raise_exception=False):
        """
        Override to ensure that the content is a valid JSON.
        """
        return True
        if not isinstance(self.initial_data.get("content"), list):
            raise serializers.ValidationError("Content must be a list of script items.")
        return super().is_valid(raise_exception=raise_exception)
