from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from colorfield.fields import ColorField

class Url(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    clicks = models.IntegerField(default=0)

    # Interstitial page settings
    interstitial1_title = models.CharField(max_length=100, default="Please wait...")
    interstitial1_message = models.TextField(default="Your link is being processed. You'll be redirected shortly.")
    interstitial1_wait_time = models.IntegerField(default=5)  # seconds
    interstitial1_background = ColorField(default='#ffffff')
    interstitial1_text_color = ColorField(default='#000000')

    interstitial2_title = models.CharField(max_length=100, default="Almost there...")
    interstitial2_message = models.TextField(default="Just one more step before you reach your destination.")
    interstitial2_wait_time = models.IntegerField(default=5)  # seconds
    interstitial2_background = ColorField(default='#ffffff')
    interstitial2_text_color = ColorField(default='#000000')

    def __str__(self):
        return f"{self.original_url} to {self.short_code}"

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def generate_short_code(self):
        characters = string.ascii_letters + string.digits
        short_code = ''.join(random.choice(characters) for _ in range(6))

        # Check if code already exists
        if Url.objects.filter(short_code=short_code).exists():
            return self.generate_short_code()
        return short_code

class ClickData(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='clicks_data')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Click on {self.url.short_code} from {self.country or 'Unknown'}"