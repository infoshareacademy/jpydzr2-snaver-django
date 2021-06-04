from django import forms

from snaver.models import Subcategory
from snaver.models import Transaction


class TransactionCreateForm(forms.ModelForm):
	class Meta:
		model = Transaction
		fields = [
			'receipt_date',
			'payee_name',
			'subcategory',
			'name',
			'amount',
			'amount',
		]
		widgets = {
			'receipt_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
			'payee_name': forms.TextInput(attrs={'class': 'form-control'}),
			'subcategory': forms.Select(attrs={'class': 'nav-item-dropdown'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'amount': forms.TextInput(attrs={'class': 'form-control'}),
			'amount': forms.TextInput(attrs={'class': 'form-control'}),
		}

	def __init__(self, user, *args, **kwargs):
		super(TransactionCreateForm, self).__init__(*args, **kwargs)

		self.fields['subcategory'].queryset = Subcategory.objects.filter(category__budget__user=user)
