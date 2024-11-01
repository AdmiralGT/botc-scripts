from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import jsonschema.exceptions
from versionfield import Version

from scripts import constants, models, validators, widgets, script_json
import json as js
import requests
import os
import jsonschema


def tagOptions():
    return models.ScriptTag.objects.filter(public=True)


class ScriptForm(forms.Form):
    name = forms.CharField(
        # Temporarily disable this constant until database migrations have occured
        # max_length=constants.MAX_SCRIPT_NAME_LENGTH, required=False, label="Script name"
        max_length=constants.MAX_SCRIPT_NAME_LENGTH, required=False, label="Script name"
    )
    author = forms.CharField(
        max_length=constants.MAX_AUTHOR_NAME_LENGTH, required=False
    )
    script_type = forms.ChoiceField(
        choices=models.ScriptTypes.choices, initial=models.ScriptTypes.FULL
    )
    version = forms.CharField(
        max_length=20, initial="1", validators=[validators.valid_version]
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
    tags = forms.ModelMultipleChoiceField(
        queryset=tagOptions(),
        to_field_name="name",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ScriptForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            json = script_json.get_json_content(cleaned_data)
        except script_json.JSONError:
            pass

        try:
            schema_version = str(os.environ.get("JSON_SCHEMA_VERSION", "v3.35.0"))
            schema_url = f"https://raw.githubusercontent.com/ThePandemoniumInstitute/botc-release/refs/tags/{schema_version}/script-schema.json"
            schema = requests.get(schema_url, timeout=2)
            try:
                schema = js.loads(schema.content)
                # Update the additionalProperties field on the Script Character object. The app doesn't enforce this and bloodstar
                # adds additional properties here.
                schema["items"]["oneOf"][0]["additionalProperties"] = True
                jsonschema.validate(json, schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ValidationError(
                    f"This is not a valid script JSON. It does not conform to the schema at {schema_url}. \
                    Error message: {e.message}"
                )
            except jsonschema.exceptions.SchemaError:
                # The schema is invalid, just continue and assume it's valid
                pass
            except KeyError:
                # Our attempt to edit the schema has failed, just continue and assume it's valid
                pass
        except requests.exceptions.Timeout:
            # We couldn't fetch the schema, just continue and assume it's valid
            pass

        if not isinstance(json, list):
            raise ValidationError(
                "This is not a valid script JSON. Script JSONs are lists of character objects."
            )
        # Author is optional so may not be entered or in JSON
        entered_author = cleaned_data.get("author", None)
        json_author = script_json.get_author_from_json(json)

        entered_name = cleaned_data.get("name", None)
        json_name = script_json.get_name_from_json(json)
        if not entered_name:
            raise ValidationError(
                "No script name provided. A name must be entered."
            )
        if json_name and entered_name:
            if json_name != entered_name:
                raise ValidationError(
                    f"Entered Name {entered_name} does not match script JSON name {json_name}"
                )

        if entered_author and json_author:
           if entered_author != json_author:
               raise ValidationError(
                   f"Entered Author {entered_author} does not match script JSON author {json_author}."
               )

        script_name = entered_name

        try:
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

        validators.validate_json(json)

        return cleaned_data


class CollectionForm(forms.ModelForm):
    class Meta:
        model = models.Collection
        fields = ["name", "description", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 17,
                    "placeholder": "Notes (enter using Markdown formatting)",
                }
            ),
        }


class AdvancedSearchForm(forms.Form):
    name = forms.CharField(max_length=constants.MAX_SCRIPT_NAME_LENGTH, required=False)
    author = forms.CharField(
        max_length=constants.MAX_AUTHOR_NAME_LENGTH, required=False
    )
    script_type = forms.ChoiceField(
        choices=models.ScriptTypes.choices, initial=models.ScriptTypes.FULL
    )
    includes_characters = forms.CharField(required=False)
    excludes_characters = forms.CharField(required=False)
    edition = forms.ChoiceField(
        choices=models.Edition.choices, initial=models.Edition.CLOCKTOWER_APP
    )
    minimum_number_of_likes = forms.IntegerField(required=False)
    minimum_number_of_favourites = forms.IntegerField(required=False)
    minimum_number_of_comments = forms.IntegerField(required=False)
    all_scripts = forms.BooleanField(
        initial=False, label="Include all Script Versions", required=False
    )
    include_hybrid = forms.BooleanField(
        initial=False, label="Include Hybrid", required=False
    )
    include_homebrew = forms.BooleanField(
        initial=False, label="Include Homebrew", required=False
    )
    tag_combinations = forms.ChoiceField(
        choices=[("AND", "AND"), ("OR", "OR")], initial="AND", widget=forms.RadioSelect
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=models.ScriptTag.objects.all().order_by("order"),
        widget=widgets.BadgePillCheckboxSelectMultiple(),
        required=False,
    )
    # We can actually get the min,max by querying the database.
    number_of_townsfolk = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )
    number_of_outsiders = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )
    number_of_minions = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )
    number_of_demons = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )
    number_of_fabled = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )
    number_of_travellers = forms.MultipleChoiceField(
        choices=[(0, 0)],
        widget=forms.SelectMultiple,
        required=False,
    )

    def __init__(
        self,
        townsfolk_choices,
        outsider_choices,
        minion_choices,
        demon_choices,
        fabled_choices,
        traveller_choices,
        *args,
        **kwargs,
    ):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        self.fields["number_of_townsfolk"].choices = townsfolk_choices
        self.fields["number_of_outsiders"].choices = outsider_choices
        self.fields["number_of_minions"].choices = minion_choices
        self.fields["number_of_demons"].choices = demon_choices
        self.fields["number_of_fabled"].choices = fabled_choices
        self.fields["number_of_travellers"].choices = traveller_choices


class UpdateDatabaseForm(forms.Form):
    # start = forms.IntegerField(
    #     min_value=0, max_value=models.ScriptVersion.objects.latest('pk').pk, required=True
    # )
    # end = forms.IntegerField(
    #     min_value=0, max_value=models.ScriptVersion.objects.latest('pk').pk, required=True
    # )
    start = forms.IntegerField(
        min_value=0, max_value=10000, required=True
    )
    end = forms.IntegerField(
        min_value=0, max_value=10000, required=True
    )

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        if start > end:
            raise ValidationError(f"Start {start} must be less than End {end}")

        if (
            start > models.ScriptVersion.objects.latest('pk').pk
            or end > models.ScriptVersion.objects.latest('pk').pk
        ):
            raise ValidationError(
                f"Trying to update database entries that don't exist. There are {models.ScriptVersion.objects.count()} scripts in the database"
            )
