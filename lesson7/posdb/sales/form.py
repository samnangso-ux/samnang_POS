# sales/forms.py

from django import forms
from .models import OrderItem


class OrderItemForm(forms.ModelForm):
    """One line item to add to an order."""
    class Meta:
        model  = OrderItem
        fields = ['product', 'quantity']

    def clean_quantity(self):
        """Validation: quantity must be at least 1."""
        qty = self.cleaned_data['quantity']
        if qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty
