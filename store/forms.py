# forms.py

from django import forms

class PaymentForm(forms.Form):
    cc_name = forms.CharField(max_length=128)
    cc_number = forms.CharField(max_length=16)
    cc_expiry = forms.CharField(max_length=4)
    cc_cvv = forms.CharField(max_length=4)
    amount = forms.DecimalField(decimal_places=2)