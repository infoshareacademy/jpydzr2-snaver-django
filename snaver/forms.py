from django import forms
from django.core.exceptions import ValidationError

from snaver.models import Subcategory
from snaver.models import SubcategoryDetails
from snaver.models import Transaction


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = [
            'name'
        ]


class TransactionCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'receipt_date',
            'payee_name',
            'subcategory',
            'name',
            'outflow',
            'inflow',
        ]
        widgets = {
            'receipt_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'outflow': forms.NumberInput(attrs={'class': 'form-control'}),
            'inflow': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(TransactionCreateForm, self).__init__(*args, **kwargs)

        self.fields['subcategory'].queryset = Subcategory.objects.filter(
            category__budget__user=user
        )

    def clean(self):
        cleaned_data = super().clean()
        outflow = cleaned_data.get("outflow")
        inflow = cleaned_data.get("inflow")

        if not outflow and not inflow:
            raise ValidationError({'outflow': 'At least one of outflow or inflow should have a value.'})

        if outflow and inflow:
            raise ValidationError({'outflow': 'Only one of outflow or inflow should have a value.'})
