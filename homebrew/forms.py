from scripts import forms as s_forms
from scripts import script_json
from homebrew import models
from django.core.exceptions import ValidationError
from versionfield import Version


class HomebrewForm(s_forms.BaseScriptForm):
    def clean(self):
        cleaned_data = super().clean()
        try:
            json = script_json.get_json_content(cleaned_data)
        except script_json.JSONError:
            pass

    def validate_script(self, name, new_version, json):
        try:
            script = models.HomebrewScript.objects.get(name=name)

            if script.owner and (script.owner != self.user):
                raise ValidationError(
                    "You are not the owner of this script and cannot upload a new version"
                )

            for script_version in script.versions.all():
                if Version(new_version) == script_version.version:
                    if script_version.content != json:
                        raise ValidationError(
                            f"Version {new_version} already exists. You cannot upload a different script with the same version number."
                        )

        except models.HomebrewScript.DoesNotExist:
            pass
