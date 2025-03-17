from django.db.models.signals import post_save
from django.dispatch import receiver
from shortener.models import ClickData
from .services import EarningService

@receiver(post_save, sender=ClickData)
def process_click_earnings(sender, instance, created, **kwargs):
    """
    When a new click is recorded, process the earnings
    """
    if created:
        EarningService.process_click_earning(instance.id)