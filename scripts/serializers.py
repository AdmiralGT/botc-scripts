from rest_framework import serializers
from scripts import models, constants, script_json


# Serializers define the API representation.
class ScriptSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="script.name")
    score = serializers.IntegerField(source="votes.count", read_only=True)

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
        fields = ["pk", "name", "content", "script_type", "version", "author", "pdf", "notes"]

    def is_createable(self, raise_exception=False) -> bool:
        """
        Check if the script can be created.
        """
        errors = []
        if models.ScriptVersion.objects.filter(
            script__name=self.validated_data.get("name"), version=self.validated_data.get("version")
        ).exists():
            errors.append("A script with this name and version already exists.")
            return False
        if not self.validated_data.get("name"):
            errors.append("Script name is required.")
            return False
        try:
            script = models.Script.objects.get(name=self.validated_data.get("name"))
            json = script_json.get_json_content(self.validated_data)
            if script.latest_version().content == json:
                errors.append("The content is identical to the latest version.")
                return False
        except models.Script.DoesNotExist:
            # It's OK if the script doesn't exist, it just means we're creating it.
            pass

        if raise_exception and errors:
            raise serializers.ValidationError(errors)
        return not errors

    def is_valid(self, create=True, raise_exception=False):
        """
        Override to ensure that the content is a valid JSON.
        """
        super().is_valid(raise_exception=raise_exception)
        errors = []
        if create:
            if self.initial_data.get("name", None) is None:
                errors.append("Script name is required.")
            if self.initial_data.get("content", None) is None:
                errors.append("Script content is required.")
            if self.initial_data.get("script_type", None) is None:
                errors.append("Script type is required.")
        if self.initial_data.get("content", None):
            content = script_json.get_json_content(self.initial_data)
            if not isinstance(content, list):
                errors.append("Content must be a list of script items.")
        if raise_exception and errors:
            raise serializers.ValidationError(errors)
        return not errors

    def is_expected_script(self, instance, raise_exception=False) -> bool:
        """
        Check if the name are version are present, that they match the expected script we're trying to update.
        """
        errors = []
        if self.validated_data.get("name") and self.validated_data.get("name") != instance.script.name:
            errors.append("You cannot change the name of an existing script.")
        if self.validated_data.get("version") and self.validated_data.get("version") != instance.version:
            errors.append("You cannot change the version of an existing script.")
        if raise_exception and errors:
            raise serializers.ValidationError(errors)
        return not errors
