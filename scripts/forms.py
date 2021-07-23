from . import models, script_json, validators
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from packaging.version import Version
import json as js


class ScriptForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    author = forms.CharField(max_length=30, required=False)
    type = forms.ChoiceField(
        choices=models.ScriptTypes.choices, initial=models.ScriptTypes.FULL
    )
    version = forms.CharField(max_length=20)
    content = forms.FileField(
        label="JSON", validators=[FileExtensionValidator(["json"])]
    )
    pdf = forms.FileField(
        label="PDF", required=False, validators=[FileExtensionValidator(["pdf"])]
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            json = get_json_content(cleaned_data)

            # Author is optional so may not be entered or in JSON
            entered_author = cleaned_data.get("author", None)
            json_author = script_json.get_author_from_json(json)
            if entered_author and json_author:
                if entered_author != json_author:
                    raise ValidationError(
                        f"Entered Author {entered_author} does not match script JSON author {json_author}"
                    )

            entered_name = cleaned_data.get("name", None)
            json_name = script_json.get_name_from_json(json)
            if not entered_name and not json_name:
                raise ValidationError(
                    f"No script name provided. A name must be entered or provided in the script JSON"
                )

            if json_name and entered_name:
                if json_name != entered_name:
                    raise ValidationError(
                        f"Entered Name {entered_name} does not match script JSON name {json_name}"
                    )

            validators.validate_json(json)

            script_name = json_name if json_name else entered_name

            script = models.Script.objects.get(name=script_name)
            new_version = cleaned_data["version"]

            if script.versions.count() == 0:
                latest_version = "0"
            else:
                latest_version = str(script.latest_version().version)

            if Version(new_version) <= Version(latest_version):
                raise ValidationError(
                    f"Version {new_version} must be newer than latest version {latest_version}"
                )

        except models.Script.DoesNotExist:
            pass


def get_json_content(data):
    json_content = data.get("content", None)
    json = js.loads(json_content.read().decode("utf-8"))
    json_content.seek(0)
    return json
