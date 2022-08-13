from django import forms


class BadgePillCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        # value.value = (
        #    '<span class="badge badge-pill badge-primary">' + value.value + "</span>"
        # )
        # label = '<span class="badge badge-pill badge-primary">' + label + "</span>"
        options = super(forms.CheckboxSelectMultiple, self).create_option(
            name, value, label, selected, index, subindex, attrs
        )
        return options
