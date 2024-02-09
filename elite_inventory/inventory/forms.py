from django import forms
from .models import deviceAttributes
from django.core.exceptions import ValidationError
import re


class DeviceAttributesForm(forms.ModelForm):
    class Meta:
        model = deviceAttributes
        fields = [
            "sku",
            "model",
            "color",
            "capacity",
            "grade",
        ]
        labels = {
            "sku": "SKU",
            "model": "Model",
            "color": "Color",
            "capacity": "Capacity",
            "grade": "Grade",
        }

    def clean_sku(self):
        sku = self.cleaned_data["sku"]
        pattern = r"^IP[A-Za-z0-9]+[A-Za-z]\d+[A-Za-z/]$"
        if not re.match(pattern, sku):
            raise forms.ValidationError(
                "SKU must follow the format 'IP<Model><Color><Capacity><Grade>'."
            )
        return sku

    def clean_model(self):
        model = self.cleaned_data["model"]
        if not model.startswith("iPhone"):
            raise forms.ValidationError("Model must start with 'iPhone'.")
        return model

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if not capacity.endswith("GB"):
            raise forms.ValidationError("Capacity must end with 'GB'.")
        return capacity
