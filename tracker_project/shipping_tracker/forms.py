from django import forms
from .models import (
    deviceAttributes,
)  # Replace 'YourModel' with the actual model you are filtering on


class FilterForm(forms.Form):
    models = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "formDropdown"}),
        choices=[
            (model, model)
            for model in deviceAttributes.objects.values_list(
                "model", flat=True
            ).distinct()
        ],
    )

    grades = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        choices=[
            (grade, grade)
            for grade in deviceAttributes.objects.values_list(
                "grade", flat=True
            ).distinct()
        ],
    )

    capacities = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        choices=[
            (cap, cap)
            for cap in deviceAttributes.objects.values_list(
                "capacity", flat=True
            ).distinct()
        ],
    )
