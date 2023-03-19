from django import forms


class BadgePillSelectMultiple(forms.SelectMultiple):
    option_template_name = "widgets/badge_pill_select_multiple.html"


class BadgePillCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = "widgets/badge_pill_checkbox_multiple.html"
