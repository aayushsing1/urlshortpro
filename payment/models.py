from django.db import models
from django.contrib.auth.models import User
from shortener.models import Url, ClickData  # Assuming your main app is named 'shortener'

class CountryRate(models.Model):
    """Model to store payment rates for different countries"""
    country_code = models.CharField(max_length=2, unique=True)
    country_name = models.CharField(max_length=100)
    rate_per_click = models.DecimalField(max_digits=6, decimal_places=4)  # Payment rate in your currency

    def __str__(self):
        return f"{self.country_name} - {self.rate_per_click}"

class UserBalance(models.Model):
    """Model to track user's balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class PaymentTransaction(models.Model):
    """Model to track payment transactions"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_details = models.JSONField(null=True, blank=True)  # Store payment details as JSON
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

class EarningRecord(models.Model):
    """Model to track individual click earnings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='earnings')
    click = models.OneToOneField(ClickData, on_delete=models.CASCADE, related_name='earning')
    amount = models.DecimalField(max_digits=6, decimal_places=4)
    country = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.url.short_code} - {self.amount}"

class PaymentSetting(models.Model):
    """Model for global payment settings"""
    min_withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    default_rate = models.DecimalField(max_digits=6, decimal_places=4, default=0.0010)  # Default rate for countries not in CountryRate
    is_payment_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Payment Settings (Min: {self.min_withdrawal_amount})"