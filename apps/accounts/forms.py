from django import forms

from apps.accounts.models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["type", "full_name", "line1", "line2", "city", "state", "postal_code", "country", "phone", "is_default"]
        widgets = {
            "type": forms.Select(attrs={"class": "select"}),
            "full_name": forms.TextInput(attrs={"class": "input"}),
            "line1": forms.TextInput(attrs={"class": "input"}),
            "line2": forms.TextInput(attrs={"class": "input"}),
            "city": forms.TextInput(attrs={"class": "input"}),
            "state": forms.TextInput(attrs={"class": "input"}),
            "postal_code": forms.TextInput(attrs={"class": "input"}),
            "country": forms.TextInput(attrs={"class": "input", "maxlength": "2", "placeholder": "US"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
            "is_default": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
