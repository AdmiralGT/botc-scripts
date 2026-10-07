from rest_framework import serializers
from rest_framework.reverse import reverse

from scripts import constants, models, script_json, upload_validators


class CollectionSerializer(serializers.ModelSerializer):
    scripts = serializers.SerializerMethodField()

    class Meta:
        model = models.Collection
        fields = ["pk", "name", "scripts"]

    def get_scripts(self, obj):
        request = self.context.get("request")
        return [
            reverse("scriptversion-detail", kwargs={"pk": script.pk}, request=request) for script in obj.scripts.all()
        ]


class ScriptSerializer(serializers.ModelSerializer):
    versions = serializers.SerializerMethodField()
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = models.Script
        fields = ["pk", "name", "versions", "latest_version"]

    def get_versions(self, obj):
        request = self.context.get("request")
        return {
            str(version.version): reverse("scriptversion-detail", kwargs={"pk": version.pk}, request=request)
            for version in obj.versions.all()
        }

    def get_latest_version(self, obj):
        request = self.context.get("request")
        latest = obj.latest_version()
        if not latest:
            return None
        return reverse("scriptversion-detail", kwargs={"pk": latest.pk}, request=request)


class VersionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="script.name")
    script_id = serializers.IntegerField(source="script.pk", read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.ScriptVersion
        fields = ["pk", "script_id", "name", "version", "script_type", "author", "content", "score"]


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
        extra_kwargs = {
            "pdf": {
                "validators": [
                    upload_validators.validate_pdf_upload_size,
                    upload_validators.validate_pdf_signature,
                ],
            },
        }

    def is_createable(self, raise_exception=False) -> bool:
        """
        Check if the script can be created.
        """
        errors = []
        if models.ScriptVersion.objects.filter(
            script__name=self.validated_data.get("name"), version=self.validated_data.get("version")
        ).exists():
            errors.append("A script with this name and version already exists.")
        if not self.validated_data.get("name"):
            errors.append("Script name is required.")
        try:
            script = models.Script.objects.get(name=self.validated_data.get("name"))
            json = script_json.get_json_content(self.validated_data)
            if script.latest_version().content == json:
                errors.append("The content is identical to the latest version.")
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
            size_errors = upload_validators.json_upload_size_errors(self.initial_data.get("content"))
            errors.extend(size_errors)
            if not size_errors:
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
