from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Url

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UrlForm(forms.ModelForm):
    class Meta:
        model = Url
        fields = ['original_url', 'interstitial1_title', 'interstitial1_message', 
                  'interstitial1_wait_time', 'interstitial1_background', 'interstitial1_text_color',
                  'interstitial2_title', 'interstitial2_message', 
                  'interstitial2_wait_time', 'interstitial2_background', 'interstitial2_text_color']
        widgets = {
            'original_url': forms.URLInput(attrs={'class': 'form-input w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'interstitial1_title': forms.TextInput(attrs={'class': 'form-input w-full px-4 py-2 border rounded'}),
            'interstitial1_message': forms.Textarea(attrs={'class': 'form-textarea w-full px-4 py-2 border rounded', 'rows': 3}),
            'interstitial2_title': forms.TextInput(attrs={'class': 'form-input w-full px-4 py-2 border rounded'}),
            'interstitial2_message': forms.Textarea(attrs={'class': 'form-textarea w-full px-4 py-2 border rounded', 'rows': 3}),
        }