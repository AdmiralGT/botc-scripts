from . import models as script_models
from django import forms
from django.db import models
from django.core.validators import FileExtensionValidator

class ScriptForm(forms.Form):
    name = forms.CharField(max_length=100)
    type = forms.ChoiceField(choices=script_models.ScriptTypes.choices)
    version = forms.CharField()
    content = forms.FileField(validators=[FileExtensionValidator(['json'])])
    pdf = forms.FileField(required=False)