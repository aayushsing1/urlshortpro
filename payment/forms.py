from django import forms
from .models import PaymentTransaction, CountryRate

class WithdrawalRequestForm(forms.ModelForm):
    # PayPal fields
    paypal_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'PayPal Email'}))

    # Bank Transfer fields
    bank_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}))
    account_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Holder Name'}))
    account_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}))
    routing_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Routing Number'}))

    # Cryptocurrency fields
    crypto_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wallet Address'}))
    crypto_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Currency (BTC, ETH, etc.)'}))

    class Meta:
        model = PaymentTransaction
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '10.00', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}, 
                                          choices=[('paypal', 'PayPal'), 
                                                  ('bank_transfer', 'Bank Transfer'),
                                                  ('crypto', 'Cryptocurrency')])
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')

        if payment_method == 'paypal':
            if not cleaned_data.get('paypal_email'):
                self.add_error('paypal_email', 'PayPal email is required for PayPal withdrawals')
        elif payment_method == 'bank_transfer':
            if not cleaned_data.get('bank_name'):
                self.add_error('bank_name', 'Bank name is required for bank transfers')
            if not cleaned_data.get('account_name'):
                self.add_error('account_name', 'Account holder name is required for bank transfers')
            if not cleaned_data.get('account_number'):
                self.add_error('account_number', 'Account number is required for bank transfers')
        elif payment_method == 'crypto':
            if not cleaned_data.get('crypto_address'):
                self.add_error('crypto_address', 'Wallet address is required for cryptocurrency withdrawals')
            if not cleaned_data.get('crypto_type'):
                self.add_error('crypto_type', 'Cryptocurrency type is required')

        return cleaned_data

class CountryRateForm(forms.ModelForm):
    class Meta:
        model = CountryRate
        fields = ['country_code', 'country_name', 'rate_per_click']
        widgets = {
            'country_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'US'}),
            'country_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'United States'}),
            'rate_per_click': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.0001', 'step': '0.0001'})
        }