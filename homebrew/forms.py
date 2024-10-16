from scripts import forms as s_forms
from scripts import script_json

class HomebrewForm(s_forms.BaseScriptForm):
    def clean(self):
        cleaned_data = super().clean()
        try:
            json = script_json.get_json_content(cleaned_data)
        except script_json.JSONError:
            pass
