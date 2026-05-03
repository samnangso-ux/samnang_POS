# sales/checkout_form.py

from django import forms
from .models import Discount


class CheckoutForm(forms.Form):
    """Apply discount to order during checkout"""
    discount_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', '— No Discount —'),
            ('staff', 'Staff Discount (10%)'),
            ('loyalty', 'Loyalty Discount (5%)'),
            ('custom', 'Custom Discount'),
        ],
        widget=forms.RadioSelect
    )
    
    custom_amount = forms.DecimalField(
        required=False,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash💵'),
            ('card', 'Card💳'),
            ('transfer', 'Bank Transfer🏦'),
        ],
        widget=forms.RadioSelect,
        initial='cash'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Order notes (optional)...'
        })
    )
