from . import models
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from packaging.version import Version


class ScriptForm(forms.Form):
    name = forms.CharField(max_length=100)
    type = forms.ChoiceField(choices=models.ScriptTypes.choices, initial=models.ScriptTypes.RAVENSWOOD)
    version = forms.CharField(max_length=20)
    content = forms.FileField(validators=[FileExtensionValidator(["json"])])
    pdf = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        try:
            script = models.Script.objects.get(name=cleaned_data["name"])
            new_version = cleaned_data["version"]

            if script.versions.count() == 0:
                latest_version = "0"
            else:
                latest_version = str(script.latest_version().version)

            if Version(new_version) <= Version(latest_version):
                raise ValidationError(f"Version {new_version} must be newer than latest version {latest_version}")    
        except models.Script.DoesNotExist:
            pass


