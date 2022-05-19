import json as js

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from versionfield import Version

from scripts import models, script_json, validators


class JSONError(Exception):
    pass


def tagOptions():
    return models.ScriptTag.objects.filter(public=True)


class ScriptForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    author = forms.CharField(max_length=30, required=False)
    script_type = forms.ChoiceField(
        choices=models.ScriptTypes.choices, initial=models.ScriptTypes.FULL
    )
    version = forms.CharField(
        max_length=20, initial="1", validators=[validators.valid_version]
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=tagOptions(),
        to_field_name="name",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    content = forms.FileField(
        label="JSON", validators=[FileExtensionValidator(["json"])]
    )
    pdf = forms.FileField(
        label="PDF", required=False, validators=[FileExtensionValidator(["pdf"])]
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 17, "placeholder": "Notes (enter using Markdown formatting)"}
        ),
    )
    anonymous = forms.BooleanField(
        required=False, initial=False, label="Upload without owning the script"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ScriptForm, self).__init__(*args, **kwargs)

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

            if script.owner and (script.owner != self.user):
                raise ValidationError(
                    "You are not the owner of this script and cannot upload a new version"
                )

            new_version = cleaned_data["version"]
            for script_version in script.versions.all():
                if Version(new_version) == script_version.version:
                    if script_version.content != json:
                        raise ValidationError(
                            f"Version {new_version} already exists. You cannot upload a different script with the same version number."
                        )

        except models.Script.DoesNotExist:
            pass
        except JSONError:
            pass


def get_json_content(data):
    json_content = data.get("content", None)
    if not json_content:
        raise JSONError("Could not read file type")
    json = js.loads(json_content.read().decode("utf-8"))
    json_content.seek(0)
    return json


class CollectionForm(forms.ModelForm):
    class Meta:
        model = models.Collection
        fields = ["name", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 17,
                    "placeholder": "Notes (enter using Markdown formatting)",
                }
            ),
        }
