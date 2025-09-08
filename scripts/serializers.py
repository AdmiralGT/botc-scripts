from rest_framework import serializers

from scripts import models, constants, script_json


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
        fields = ["pk","name","content", "script_type", "version", "author", "pdf", "notes"]

    def is_createable(self, raise_exception=False) -> bool:
        """
        Check if the script can be created.
        """
        if models.ScriptVersion.objects.filter(script__name=self.validated_data.get("name"),version=self.validated_data.get("version")).exists():
            if raise_exception:
                raise serializers.ValidationError("A script with this name and version already exists.")
            return False
        if not self.validated_data.get("name"):
            if raise_exception:
                raise serializers.ValidationError("Script name is required.")
            return False
        return True
    

    def is_expected_script(self, raise_exception=False) -> bool:
        """
        Check if the script we have the expected one.
        """
        if not self.instance:
            if raise_exception:
                raise serializers.ValidationError("Could not find request ScriptVersion instance.")
            return False

        if self.instance.script.name != self.data.get("name"):
            if raise_exception:
                raise serializers.ValidationError("Attempting to update a script with a different name.")
            return False


    def is_valid(self, raise_exception=False):
        """
        Override to ensure that the content is a valid JSON.
        """
        super().is_valid(raise_exception=raise_exception)
        errors = []
        if self.initial_data.get("name", None) is None:
            errors.append("Script name is required.")
        if self.initial_data.get("content", None) is None:
            errors.append("Script content is required.")
        if self.initial_data.get("script_type", None) is None:
            errors.append("Script type is required.")
        content = script_json.get_json_content(self.initial_data)
        if not isinstance(content, list):
            errors.append("Content must be a list of script items.")
        if raise_exception and errors:
            raise serializers.ValidationError(errors)
        return True
